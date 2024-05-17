#!/usr/bin/env python3

import typer
import fsspec
import geopandas
import xarray as xr
from dask.delayed import delayed
from pathlib import Path
from datetime import datetime
from time import perf_counter
from dask.distributed import Client
from typing_extensions import Annotated
from typing import List
import time


"""
This script collects AORC v1.1 forcing data from a remote Zarr store, 
clips it to a shapefile, slices it by time, and saves it as a NetCDF file.

These data are available at the following URL: s3://noaa-nwm-retrospective-3-0-pds/CONUS

"""


class catchtime:
    def __init__(self, msg):
        self.msg = msg + "..."

    def __enter__(self):
        print(self.msg, end="", flush=True)
        self.start = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.start
        self.readout = f"{self.time:.3f} seconds"
        print(self.readout)


@delayed
def load_zarr(s3path: str) -> xr.Dataset:
    """
    Load a Zarr dataset from an S3 bucket.

    Parameters
    ==========
    s3path: str
        URL of the S3 bucket

    Returns
    =======
    Xarray Dataset
    """

    return xr.open_zarr(fsspec.get_mapper(s3path, anon=True), consolidated=True)


@delayed
def clip_zarr(ds: xr.Dataset, gdf: geopandas.GeoDataFrame) -> xr.Dataset:
    """
    Clip a Zarr dataset to a geopandas GeoDataFrame.

    Parameters
    ==========
    ds: xr.Dataset
      Zarr dataset
    gdf: geopandas.GeoDataFrame
      GeoDataFrame to clip the dataset

    Returns
    =======
    Xarray Dataset

    """
    # Need to set the the crs in the dataset using rioxarray.
    # The crs is obtained from the 'esri_pe_string' attribute
    # within the 'crs' variable.
    ds.rio.set_crs(ds.crs.attrs["esri_pe_string"])
    ds.rio.write_crs(inplace=True)

    # Transform the input watershed shapefile to the same
    # coordinate system of the xarray dataset. This is necessary
    # to ensure that data for the correct spatial location is extracted.
    gdf = gdf.to_crs(ds.rio.crs)

    # Perform clip operation to isolate the region of the zarr
    # dataset that intersects with the input watershed geometry.
    # Using 'all_touched=True' to select all grid cells that are within or touch
    # the geometry, This is especially important for small geometries.
    return ds.rio.clip(
        gdf.geometry.values,
        gdf.crs,
        all_touched=True,
        drop=True,
        invert=False,
        from_disk=True,
    )


@delayed
def slice_zarr(ds: xr.Dataset, start_date: datetime, end_date: datetime) -> xr.Dataset:
    """
    Slice an Xarray dataset by time.

    Parameters
    ==========
    ds: xr.Dataset
      Xarr dataset
    start_date: datetime
      start of the date range for which data will be collected

    Returns
    =======
    Xarray Dataset

    """
    ds = ds.sel(time=slice(start_date, end_date))
    return ds


@delayed
def save_to_file(ds: xr.Dataset, output_file: Path, format: str = "NETCDF4") -> Path:
    """
    Save an Xarray dataset to a NetCDF file.

    Parameters
    ==========
    ds: xr.Dataset
      Xarray dataset
    output_file: Path
      local file path to save the collected forcing data
    format: str
      format of the NetCDF file

    Returns
    =======
    Path

    """
    # Save the xarray dataset to NetCDF format. Using
    # NetCDF 4 by default, but this can be changed if desired.
    ds.to_netcdf(output_file, format=format, engine="netcdf4")
    return output_file


@delayed
def process_data(
    bucket_url: str,
    region: str,
    gdf: geopandas.GeoDataFrame,
    variable: str,
    start_date: datetime,
    end_date: datetime,
) -> xr.Dataset:
    """
    Load, clip, and slice a Zarr dataset.

    Parameters
    ==========
    bucket_url: str
      URL of the S3 bucket
    region: str
      region of the data
    gdf: geopandas.GeoDataFrame
      GeoDataFrame to clip the dataset
    variable: str
      variable to process
    start_date: datetime
      start of the date range for which data will be collected
    end_date: datetime
      end of the date range for which data will be collected

    Returns
    =======
    Xarray Dataset

    """
    s3path = f"{bucket_url}/{region}/zarr/forcing/{variable}.zarr"
    ds = load_zarr(s3path)
    ds = clip_zarr(ds, gdf)
    ds = slice_zarr(ds, start_date, end_date)
    return ds.compute()


@delayed
def merge_datasets(dss: List[xr.Dataset]) -> xr.Dataset:
    """
    Merge a list of Xarray datasets.

    Parameters
    ==========
    dss: List[xr.Dataset]
      list of Xarray datasets

    Returns
    =======
    Xarray Dataset
    """

    return xr.merge([ds.compute() for ds in dss])


def main(
    start_date: Annotated[
        datetime,
        typer.Argument(help="start of the date range for which data will be collected"),
    ],
    end_date: Annotated[
        datetime,
        typer.Argument(help="end of the date range for which data will be collected"),
    ],
    shapefile: Annotated[Path, typer.Argument(help="path to shapefile")],
    bucket_url: Annotated[
        str,
        typer.Argument(help="path to S3 bucket"),
    ] = "s3://noaa-nwm-retrospective-3-0-pds",
    output_file: Annotated[
        Path,
        typer.Argument(
            help="local file path to save the collected forcing data",
        ),
    ] = Path("forcing.nc"),
    n_workers: Annotated[
        int, typer.Option(help="Number of dask workers to use for computation")
    ] = 2,
    worker_memory: Annotated[
        int,
        typer.Option(
            help="Maximum amount of memory in GB that will be available to each worker",
        ),
    ] = 4,
    verbose: Annotated[bool, typer.Option(help="Turn on verbose stdoout")] = False,
):
    """
    Collect AORC v1.1 forcing data from a remote Zarr store, clip it to a shapefile,
    then save the result to a NetCDF file.

    Parameters
    ==========
    start_date: datetime
        start of the date range for which data will be collected
    end_date: datetime
        end of the date range for which data will be collected
    shapefile: Path
        path to a shapefile that will be used to spatially clip the forcing data
    bucket_url: str
        path to S3 bucket where the forcing data is stored
    output_file: Path
        local file path to save the collected forcing data
    n_workers: int
        Number of dask workers to use for computation
    worker_memory: int
        Maximum amount of memory in GB that will be available to each worker
    verbose: bool
        Turn on verbose stdout
    """

    st = time.time()

    # adjust the dask cluster
    client.cluster.scale(n=n_workers, memory=f"{worker_memory}GB")

    # TODO: make region configurable
    # set the region as one of the following: 'CONUS', 'Hawaii', 'Puerto Rico', 'Alaska'
    region = "CONUS"

    # TODO: make variables configurable
    variables = ["lwdown", "precip", "psfc", "q2d", "swdown", "t2d", "u2d", "v2d"]

    futures = []
    # read the shapefile that will be used to clip the data
    scattered_gdf = client.scatter(geopandas.read_file(shapefile))

    # loop through each variable and process the data
    for variable in variables:

        futures.append(
            process_data(
                bucket_url, region, scattered_gdf, variable, start_date, end_date
            )
        )

    merged_ds = merge_datasets(futures)
    save_to_file(merged_ds, output_file, format="NETCDF4").compute()

    print(f"Elapsed time:{time.time() - st:2f} seconds")


if __name__ == "__main__":
    client = Client(n_workers=1)
    typer.run(main)
