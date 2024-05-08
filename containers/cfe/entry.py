#!/usr/bin/env python3

import sys
import dask
import typer
import pyproj
import xarray
import pandas
import logging
import geopandas
from pathlib import Path
from datetime import datetime
from dask.distributed import Client
from geocube.api.core import make_geocube

from pydantic_yaml import to_yaml_str

from config_generators import cfe, troute


# set logging level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
logger.addHandler(handler)


def main(
    geopackage: Path = typer.Argument(..., help="Path to NextGen Geopackage"),
    forcing: Path = typer.Argument(..., help="Path to forcing netcdf"),
    cfe_attrs_path: Path = typer.Argument(
        "cfe_noahowp_attributes.csv", help="Path to cfe attributes"
    ),
    output_dir: Path = typer.Argument("output", help="Directory to save output"),
    n_workers: int = typer.Argument(2, help="Number of dask workers"),
    worker_memory: int = typer.Argument(4, help="Max memory per worker (GB)"),
    verbose: bool = typer.Option(default=False, help="Turn on verbose stdoout"),
):

    # create output directory
    if not output_dir.exists():
        output_dir.mkdir()

    # set logging level
    if verbose:
        logger.setLevel(logging.INFO)

    # adjust the dask cluster
    logger.info(f"{n_workers} workers, {worker_memory}GB memory")
    client.cluster.scale(n=n_workers, memory=f"{worker_memory}GB")
    logger.info(client.dashboard_link)

    logger.info("Loading - forcing and geospatial")
    # load data and scatter
    ds, gdf = load_data(forcing, geopackage)

    logger.info("Scattering - forcing and geospatial")
    scattered_ds = client.scatter(ds, broadcast=True)
    scattered_gdf = client.scatter(gdf, broadcast=True)

    # prepare zonal stats and scatter
    logger.info("Computing - zonal statistics")
    zonal_ds = prepare_zonal(scattered_ds, scattered_gdf).compute()
    logger.info("Scattering - zonal statistics")
    scattered_zonal_ds = client.scatter(zonal_ds, broadcast=True)

    # clean up
    del scattered_ds
    del scattered_gdf

    logger.info("Computing - basin averages")
    # compute basin averaged values
    delayed = delayed_zonal_computation(scattered_zonal_ds)
    ds = delayed.compute()

    # clean up
    del scattered_zonal_ds

    # convert cat from float to string
    ds = ds.assign_coords({"cat": ds.cat.astype(int).astype(str)})
    results_scattered = client.scatter(ds, broadcast=True)

    logger.info("Saving - output to csv")
    forcing_path = Path(output_dir / "forcing")

    # write output to csv
    if not forcing_path.exists():
        forcing_path.mkdir()

    delayed_write = []
    for cat_id in ds.cat.values:
        delayed_write.append(save_to_csv(results_scattered, cat_id, forcing_path))
    _ = dask.compute(delayed_write)

    # compute synthetic data for missing catchments
    logger.info("Computing - synthetic forcing for missing catchments")
    computed_catchments = list(ds.cat.values)
    idx = ds.time.values
    for known_id in gdf["id"].values:
        _id = known_id.split("-")[-1]
        if _id not in computed_catchments:
            logger.info(f"----> Creating forcing for {known_id}")
            synthetic_df = pandas.DataFrame(
                0,
                index=idx,
                columns=[
                    "APCP_surface",
                    "DLWRF_surface",
                    #'PRES_surface',
                    "SPFH_2maboveground",
                    "DSWRF_surface",
                    "TMP_2maboveground",
                    "UGRD_10maboveground",
                    "VGRD_10maboveground",
                    "precip_rate",
                ],
            )
            # write to file
            with open(f"{forcing_path}/{known_id}.csv", "w") as f:
                synthetic_df.to_csv(f, index_label="time")

    logger.info("Creating - realization files")
    create_realization(
        pandas.to_datetime(ds.time.values.min()).to_pydatetime(),
        pandas.to_datetime(ds.time.values.max()).to_pydatetime(),
        geopackage,
        cfe_attrs_path,
        output_dir,
    )


def load_data(forcing, geopackage):
    ds = load_ds(forcing)
    gdf = load_gdf(geopackage)
    return ds, gdf


def load_ds(forcing):

    # load forcing data
    ds = xarray.open_dataset(forcing)

    return ds


def load_gdf(geopackage):

    # load hydrofabric
    gdf = geopandas.read_file(geopackage, layer="divides")

    # convert these data into the projection of our forcing data
    # this assumes that we're using AORC forcing.
    # TODO: generalize this to use whatever projection is defined in the
    # forcing dataset
    target_crs = pyproj.Proj(
        proj="lcc",
        lat_1=30.0,
        lat_2=60.0,
        lat_0=40.0000076293945,
        lon_0=-97.0,
        a=6370000,
        b=6370000,
    )
    gdf = gdf.to_crs(target_crs.crs)

    return gdf


@dask.delayed
def prepare_zonal(in_ds, gdf):

    # create zonal id column
    gdf["cat"] = gdf.id.str.split("-").str[-1].astype(int)

    # set the aorc crs.
    # TODO: This should be set when the dataset is saved, not here.
    in_ds = in_ds.rio.write_crs("EPSG:4326", inplace=True)

    # create a grid for the geocube
    out_grid = make_geocube(
        vector_data=gdf,
        measurements=["cat"],
        like=in_ds,  # ensure the data are on the same grid
    )

    # add the catchment variable to the original dataset
    in_ds = in_ds.assign_coords(cat=(["latitude", "longitude"], out_grid.cat.data))

    return in_ds


@dask.delayed
def delayed_zonal_computation(ds):
    return ds.groupby(ds.cat).mean()


@dask.delayed
def save_to_csv(results, cat_id, output_dir):
    fname = f"cat-{int(cat_id)}"
    with open(f"{output_dir}/{fname}.csv", "w") as f:
        df = results.sel(dict(cat=cat_id)).to_dataframe()
        df.fillna(0.0, inplace=True)
        df["precip_rate"] = df.APCP_surface
        df.to_csv(
            f,
            columns=[
                "APCP_surface",
                "DLWRF_surface",
                "DSWRF_surface",
                #                                'PRES_surface',
                "SPFH_2maboveground",
                "TMP_2maboveground",
                "UGRD_10maboveground",
                "VGRD_10maboveground",
                "precip_rate",
            ],
        )


def create_realization(
    start_time,
    end_time,
    geopackage,
    cfe_attrs_path,
    output_dir,
    routing_timestep_in_sec=300,
):

    outpath = Path(output_dir / "config")
    if not outpath.exists():
        outpath.mkdir()

    # generate T-Route configuration
    tconf = troute.create_troute_configuration(
        simulation_start=start_time,
        simulation_end=end_time,
        timestep_in_seconds=routing_timestep_in_sec,
        geopackage_path=geopackage,
        input_data_path=Path("/ngen/data/results"),
        output_file=output_dir / "config/ngen.yaml",
    )

    # need to fix some errors in the T-ROUTE pydantic classes

    # network topology parameters are not set correctly when using the T-Route
    # pydantic classes. Load the class and manually remove "mainstem" from
    # the columns dictionary.
    # ----
    #     network_topology_parameters -> supernetwork_parameters -> columns -> mainstem
    #       extra fields not permitted (type=value_error.extra)
    _ = tconf.network_topology_parameters.supernetwork_parameters.columns.pop(
        "mainstem"
    )

    # datetimes are not formated properly in the compute_parameters class
    # ----
    # compute_parameters -> restart_parameters -> start_datetime
    #   datetime field must be specified as `datetime.datetime` object or string with
    #   format ('%Y-%m-%d_%H:%M', '%Y-%m-%d_%H:%M:%S', '%Y-%m-%d %H:%M',
    #   '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S') (type=value_error)
    dt = tconf.compute_parameters.restart_parameters.start_datetime
    tconf.compute_parameters.restart_parameters.start_datetime = datetime.strftime(
        dt, "%Y-%m-%d %H:%M:%S"
    )

    with open(outpath / "ngen.yaml", "w") as f:
        f.write(to_yaml_str(tconf, by_alias=True, exclude_none=True, sort_keys=False))

    # create CFE configuration
    cfe.create_global_cfe_realization(
        cfe_attrs_path, start_time, end_time, output_dir / "config"
    )


if __name__ == "__main__":

    # TODO; move n_workers and memory limit to inputs.
    client = Client(n_workers=1)
    typer.run(main)
