#!/usr/bin/env python3

import s3fs  
import fsspec  
import pandas  
import xarray as xr
import rioxarray  
import zarr  
import geopandas  
import boto3  
from time import perf_counter
from dask.distributed import Client  
from dask.diagnostics import ProgressBar


class catchtime:
    def __init__(self, msg):
        self.msg = msg + '...'
    def __enter__(self):
        print(self.msg, end='', flush=True)
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.start
        self.readout = f'{self.time:.3f} seconds'
        print(self.readout)

def collect_data():
    bucket_url = 's3://aorc-v1.1-zarr-1-year/'
    key='AKIATL6IACWUNBCC4455'  
    secret='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'  
    
    with catchtime('loading zarr'):
        ds = xr.open_zarr(fsspec.get_mapper(bucket_url,
                              anon=False,
                              key=key,
                              secret=secret), consolidated=True)
    
    with catchtime('clipping zarr'):
        gdf = geopandas.read_file('watershed.shp')
        ds.rio.write_crs('EPSG:4326', inplace=True)
        ds = ds.rio.clip(gdf.geometry.values,
                          gdf.crs,
                          drop=True,
                          invert=False, from_disk=True)  
                  
    
    with catchtime('slicing zarr'):
        ds = ds.sel(time=slice('2020-01-01', '2020-01-2')) 
    
    with catchtime('saving netcdf'):
        write_job = ds.to_netcdf('results.nc',
                             mode='w',
                             format='NETCDF4',
                             compute=False)
        write_job.compute()


if __name__ == '__main__':
    client = Client(n_workers=2, memory_limit='4GB')
    collect_data()
