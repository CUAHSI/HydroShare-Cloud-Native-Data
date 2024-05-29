#!/usr/bin/env python3


"""
This script provides helper functions for submitting jobs to CUAHSI's Argo Workflow server.
"""

from __future__ import print_function

import swagger_client
from pprint import pprint
from datetime import datetime
from swagger_client.rest import ApiException

import time
import geopandas
import ipyleaflet
from pathlib import Path
from sidecar import Sidecar
from ipywidgets import Layout

import shapely
from shapely.geometry import box
#import pynhd as nhd

import textwrap
from tabulate import tabulate

import warnings
warnings.filterwarnings("ignore")


class ArgoAPI():
    def __init__(self, token, namespace='workflows'):
        self.bearer_token = token
        self.namespace = namespace
        self.configuration = swagger_client.Configuration()
        self.configuration.api_key['Authorization'] = token
        self.configuration.host = "https://workflows.argo.cuahsi.io"
        
        self.template_api_instance = None
        self.workflow_api_instance = None
        self.info_api_instance = None

        self.__configure_client()

        # print out some user info
        info = self.user_info()
        table_data = [['Status', 'Connected'],
                      ['Name', info['name']],
                      ['Email', info['email']]]
        print('User Info')
        print(tabulate(table_data, tablefmt='rounded_outline'))
        
        
        
    def __configure_client(self):
        
        self.template_api_instance = swagger_client.WorkflowTemplateServiceApi(swagger_client.ApiClient(self.configuration))
        
        self.workflow_api_instance = swagger_client.WorkflowServiceApi(swagger_client.ApiClient(self.configuration))
        
        self.info_api_instance = swagger_client.InfoServiceApi(swagger_client.ApiClient(self.configuration))

    def user_info(self):
        info = self.info_api_instance.info_service_get_user_info()
        return {'name' : info.name,
                'email': info.email}

    def list_workflows(self, return_json=False):   
        try:
            api_response = self.template_api_instance.workflow_template_service_list_workflow_templates(self.namespace)

            if not return_json:
                return [item.metadata.name for item in api_response.items]

            return api_response
        
        except ApiException as e:
            print("Exception when calling WorkflowTemplateServiceApi->workflow_template_service_list_workflow_templates: %s\n" % e)
            return []

    def get_workflow_metadata(self, name):
        workflows = self.list_workflows(return_json=True)
        return next((item for item in workflows.items if item.metadata.name == name), None)
        

    def get_workflow_parameters(self, name):
        workflow = self.get_workflow_metadata(name)
        if workflow is not None:
            return workflow.spec.arguments.parameters
        return None

    def __submit_workflow_body(self, template_name: str, parameters: dict):
        parameters_list = [f"{key}={value}" for key, value in parameters.items()]
        return {
            "resourceKind": "WorkflowTemplate",
            "resourceName": template_name,
            "submitOptions": {
                "parameters":parameters_list,
            }
        }
    def submit_workflow(self, name, parameters):
        body = self.__submit_workflow_body(name, parameters)
        return self.workflow_api_instance.workflow_service_submit_workflow(self.namespace, body).metadata.name
    
    def get_workflow_status(self, name):
        submitted_workflow = self.workflow_api_instance.workflow_service_get_workflow(self.namespace, name)
        phase    = submitted_workflow.status.phase
        progress = submitted_workflow.status.progress
        return progress, phase
    
    def display_workflow_metadata(self, name):
        table_data = []
        meta = self.get_workflow_metadata(name).metadata
        if hasattr(meta, 'annotations'):
            for k, v in meta.annotations.items():
                if (label := k.split('/'))[0] == 'cuahsi':
                    wrapped_val = textwrap.wrap(v, 80)
                    wrapped_label = [label[1]] + ['\n']*(len(wrapped_val)-1)
                    for i in range(0, len(wrapped_label)):
                        table_data.append([wrapped_label[i], wrapped_val[i]])
        print(tabulate(table_data, headers=['Key', 'Value'], tablefmt='rounded_outline'))        
    
    def display_workflow_parameters(self, name):
        params = self.get_workflow_parameters(name)
        table_data = []
        for d in params:
            wrapped_desc = textwrap.wrap(d.description, 80)
            wrapped_label = [d.name] + ['\n']*(len(wrapped_desc)-1)
            wrapped_default = [d.value] + ['\n']*(len(wrapped_desc)-1)
            for i in range(0, len(wrapped_label)):
                table_data.append([wrapped_label[i], wrapped_default[i], wrapped_desc[i]])
            #table_data.append([d.name, d.value, d.description])
        print(tabulate(table_data, headers=['Variable', 'Default', 'Description'], tablefmt='rounded_outline'))
        


class SideCarMap():
    def __init__(self, basemap=ipyleaflet.basemaps.OpenStreetMap.Mapnik, gdf=None, plot_gdf=False):
        self.selected_id = None
        self.map = None
        self.basemap = basemap
        self.gdf = gdf
        self.plot_gdf = False

    def display_map(self):
        defaultLayout=Layout(width='960px', height='940px')

        self.map = ipyleaflet.Map(
        basemap=ipyleaflet.basemap_to_tiles(ipyleaflet.basemaps.OpenStreetMap.Mapnik, layout=defaultLayout),
            center=(45.9163, -94.8593),
            zoom=9,
            scroll_wheel_zoom=True,
            tap=False
            )
        
        
        # add USGS Gages
        self.map.add_layer(
            ipyleaflet.WMSLayer(
                url='http://arcgis.cuahsi.org/arcgis/services/NHD/usgs_gages/MapServer/WmsServer',
                layers='0',
                transparent=True,
                format='image/png',
                min_zoom=8,
                max_zoom=18,
                )
        )
        
        # add NHD+ Reaches
        self.map.add_layer(
            ipyleaflet.WMSLayer(
                url='https://hydro.nationalmap.gov/arcgis/services/nhd/MapServer/WMSServer',
                layers='6',
                transparent=True,
                format='image/png',
                min_zoom=8,
                max_zoom=18,
                )
        )

        # add features from geopandas if they are provided
        if self.gdf is not None:

            # update the map center point
            polygon = box(*self.gdf.total_bounds)
            approx_center = (polygon.centroid.y, polygon.centroid.x)
            self.map.center = approx_center

            # bind the map handler function
            self.map.on_interaction(self.handle_map_interaction)

            if self.plot_gdf:
                print('Loading GDF Features...', end='')
                st = time.time()
                geo_data = ipyleaflet.GeoData(geo_dataframe = self.gdf,
                       style={'color': 'blue', 'opacity':0.5, 'weight':1.9,}
                      )
                self.map.add(geo_data)

                print(f'{time.time() - st:0.2f} sec')

        sc = Sidecar(title='NHD+ River Reaches')
        with sc:
            display(self.map)
        
    def handle_map_interaction(self, **kwargs):
    
        if kwargs.get('type') == 'click':
            print(kwargs)
            lat, lon = kwargs['coordinates']
            print(f'{lat}, {lon}')
            
            # query the reach nearest this point
            point = shapely.Point(lon, lat)

            # buffer the selected point by a small degree. This
            # is a hack for now and Buffer operations should only
            # be applied in a projected coordinate system in the future.
            print('buffering')
            pt_buf = point.buffer(0.001) 

            try:
                # remove the previously selected layers
                while len(self.map.layers) > 3:
                    self.map.remove(self.map.layers[-1]);
                
                # query the FIM reach that intersects with the point
                print('intersecting...')
                mask = self.gdf.intersects(pt_buf)
                print(f'found {len(self.gdf.loc[mask])} reaches')
                print('saving selected...')
                self.selected(value=self.gdf.loc[mask].iloc[0])

                # highlight this layer on the map
                wlayer = ipyleaflet.WKTLayer(
                    wkt_string=self.selected().geometry.wkt,
                    style={'color': 'green', 'opacity':1, 'weight':2.,})
                self.map.add(wlayer)
                
            except Exception: 
                print('Could not find reach for selected area')

    # getter/setter for the selected reach
    def selected(self, value=None):
        if value is None:
            if self.selected_id is None:
                print('No reach is selected.\nUse the map interface to select a reach of interest')
            else:
                return self.selected_id
        else:
            self.selected_id = value

