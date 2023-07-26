#!/usr/bin/env python3

from datetime import datetime

import numpy
import xarray
import pyproj
import geopandas
import rioxarray
from s3fs import S3FileSystem
from dask.distributed import Client
from kerchunk.combine import MultiZarrToZarr

import logging
from pathlib import Path
from typer import run, Argument, Option
from typing_extensions import Annotated


def main(
        start_date: Annotated[
            datetime, Argument(
                help="start of time range to collect data")],
        end_date: Annotated[
            datetime, Argument(
                help="end of time range to collect data")],
        shapefile: Annotated[
            str, Argument(
                help="path to shapefile that will be used to clip the aorc")],
        outdir: Annotated[
            str, Argument(
                help="path to save output AORC data")] = './aorc',
        s3_bucket: Annotated[
        str, Argument(
        help="url of the s3 bucket containing AORC forcing data")
        ] = 's3://ciroh-nwm-zarr-retrospective-data-copy/noaa-nwm-retrospective-2-1-zarr-pds/forcing/',
        verbose: Annotated[bool, Option("--verbose")] = False,
):
    # set verbosity level
    if verbose:
        logging.basicConfig(level=logging.INFO)

    client = Client(n_workers=6, memory_limit='2GB') # per worker

    # load the zarr headers into an xarray dataset
    ds = load_zarr(start_date, end_date, s3_bucket)

    # add spatial metadata
    ds = add_spatial_metadata(ds,
            spatial_source='http://thredds.hydroshare.org/thredds/dodsC/hydroshare/resources/2a8a3566e1c84b8eb3871f30841a3855/data/contents/WRF_Hydro_NWM_geospatial_data_template_land_GIS.nc')

    # clip the data spatially to the extent of the input watershed
    ds = clip_aorc_by_shapefile(ds, shapefile) 
    
    # save to hourly files
    outpath = Path(outdir)
    outpath.mkdir(parents=True, exist_ok=True)
    times, datasets = zip(*ds.groupby("time"))
    paths = []
    for t in times:
        ts = datetime.utcfromtimestamp(t.astype(int) * 1e-9)
        paths.append(f'{outpath}/{ts.strftime("%Y%m%d%H%M")}.LDASIN_DOMAIN1')
    logging.info('Saving AORC to disk')
    xarray.save_mfdataset(datasets, paths, format='NETCDF4')

    logging.info('Operation Completed Successfully')

def load_zarr(start_date: datetime,
              end_date: datetime,
              s3bucket: str) -> xarray.Dataset:
    """
    Creates an xarray Dataset from data stored in s3.
 
    Parameters
    ----------
    start_date: datetime.datetime
        start datetime for collecting aorc data.
    end_date: datetime.datetime
        end datetime for collecting aorc data.
    s3bucket: str
        url to the s3 bucket containing aorc data.

    Returns
    -------
    xarray.DataSet
        An xarray dataset object containing the metadata from the input
        headers provided.
 
  """
    # create an instace of the S3FileSystem class from s3fs
    s3 = S3FileSystem(anon=True)
    
    # todo: this doesn't seem super efficient. A regex solution would probably
    # be better but a quick search indicated that it's not supported
    # in the s3fs library
    year = start_date.year
    headers = [] # list to store json headers in
    while year <= end_date.year:

        # list files in bucket
        logging.info(f'Collecting files for {year}')
        all_files = s3.ls(f'{s3bucket}{year}')  
        
        for f in all_files:
            parts = f.split('/')
            dt = datetime.strptime(parts[-1].split('.')[0], '%Y%m%d%H')

            if dt < start_date:
                # continue until the start time is reached
                continue

            if dt > end_date:
                # exit early
                break

            # save the url to the json header
            parts[0] += '.s3.amazonaws.com'
            parts.insert(0, 'https:/')
            headers.append('/'.join(parts))
        
        # increment year
        year += 1


    logging.info(f'Found {len(headers)} files')

    logging.info('Loading data using MultiZarrToZarr')
    mzz = MultiZarrToZarr(headers,
            remote_protocol='s3',
            remote_options={'anon':True},
            concat_dims=['valid_time'])

    # open the dataset
    d = mzz.translate()
    backend_args = {"consolidated": False, "storage_options": {"fo": d}, "consolidated": False}
    ds = xarray.open_dataset("reference://", engine="zarr", backend_kwargs=backend_args)
   
    # squeeze along the Time dimension to remove it since we have valid_time
    ds = ds.squeeze(dim='Time')
    
    # rename dimensions
    ds = ds.rename({'valid_time': 'time', 'south_north':'y', 'west_east':'x'})

    # rechunk the dataset to solve the memory limit issue
    ds = ds.chunk(chunks={'time': 1})

    logging.info('Dataset loaded successfully')
    logging.info(f'{ds.dims}')
   
    return ds



def add_spatial_metadata(ds: xarray.Dataset,
                         spatial_source: str) -> xarray.Dataset:
    """
    Adds missing spatial metadata to the AORC forcing data.

    Parameters
    ----------
    ds: xarray.Dataset
        Input dataset for which spatial metadata will be added to.

    spatial_source: str
        Path to the file used to provide the missing spatial metadata. For 
        Example: WRF_Hydro_NWM_geospatial_data_template_land_GIS.nc.

    Returns 
    -------
    xarray.Dataset
        An xarray dataset with spatial metadata.

    """

    # load the spatial metadata source
    logging.info(f'Loading spatial metadata from {spatial_source}')
    ds_meta = xarray.open_dataset(spatial_source)

    
    logging.info(f'Adding spatial metadata')
    # create meshgrid for x,y dimensions
    x = ds_meta.x.values
    y = ds_meta.y.values
    X, Y = numpy.meshgrid(x, y)

    # define the input crs
    wrf_proj = pyproj.Proj(proj='lcc',
                           lat_1=30.,
                           lat_2=60., 
                           lat_0=40.0000076293945, lon_0=-97., # Center point
                           a=6370000, b=6370000)

    # define the output crs
    wgs_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    # transform X, Y into Lat, Lon
    transformer = pyproj.Transformer.from_crs(wrf_proj.crs, wgs_proj.crs)
    lon, lat = transformer.transform(X, Y)

    ds = ds.assign_coords(lon = (['y', 'x'], lon))
    ds = ds.assign_coords(lat = (['y', 'x'], lat))
    ds = ds.assign_coords(x = x)
    ds = ds.assign_coords(y = y)

    ds.x.attrs['axis'] = 'X'
    ds.x.attrs['standard_name'] = 'projection_x_coordinate'
    ds.x.attrs['long_name'] = 'x-coordinate in projected coordinate system'
    ds.x.attrs['resolution'] = 1000.  # cell size

    ds.y.attrs['axis'] = 'Y' 
    ds.y.attrs['standard_name'] = 'projection_y_coordinate'
    ds.y.attrs['long_name'] = 'y-coordinate in projected coordinate system'
    ds.y.attrs['resolution'] = 1000.  # cell size

    ds.lon.attrs['units'] = 'degrees_east'
    ds.lon.attrs['standard_name'] = 'longitude' 
    ds.lon.attrs['long_name'] = 'longitude'

    ds.lat.attrs['units'] = 'degrees_north'
    ds.lat.attrs['standard_name'] = 'latitude' 
    ds.lat.attrs['long_name'] = 'latitude'

    # add crs to netcdf file
    ds.rio.write_crs(ds_meta.crs.attrs['spatial_ref'], inplace=True
                ).rio.set_spatial_dims(x_dim="x",
                                       y_dim="y",
                                       inplace=True,
                                       ).rio.write_coordinate_system(inplace=True);
   
    logging.info(f'Successfully added spatial metadata to Dataset')

    return ds


def clip_aorc_by_shapefile(ds: xarray.Dataset,
                           shapefile: str) -> xarray.Dataset:
    """
    Performs spatial clip of data using bounding box.

    Parameters
    ----------
    ds: xarray.Dataset
        The input dataset that will be clipped

    shapefile: str
        path to an ESRI Shapefile that will be used to clip the AORC data.


    Returns
    -------
    xarray.Dataset
        An xarray dataset that has been clipped to the input Shapefile.
    """
    
    # load shapefile using geopandas and convert to aorc srs
    logging.info('Reading input Shapefile and transforming srs')
    gdf = geopandas.read_file(shapefile)

    # convert these data into the projection of our forcing data
    target_crs = pyproj.Proj(proj='lcc',
                       lat_1=30.,
                       lat_2=60., 
                       lat_0=40.0000076293945, lon_0=-97., # Center point
                       a=6370000, b=6370000) 

    gdf = gdf.to_crs(target_crs.crs)

    # clip AORC to the extent of the hydrofabric geometries
    logging.info('Clipping Dataset to Shapefile extent')
    ds = ds.rio.clip(gdf.geometry.values,
                 gdf.crs,
                 drop=True,
                 invert=False, from_disk=True)

    logging.info('Successfully clipped Dataset')
    return ds

if __name__ == "__main__":
    run(main)
