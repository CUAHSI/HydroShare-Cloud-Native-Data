#!/usr/bin/env python3

import sys
import datetime
import logging
from pathlib import Path
from pydantic_yaml import to_yaml_str

from troute.config import (
    config,
    logging_parameters,
    compute_parameters,
    network_topology_parameters,
    output_parameters,
    types,
)

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def create_troute_configuration(
    simulation_start: datetime.datetime,
    simulation_end: datetime.datetime,
    timestep_in_seconds: int,
    geopackage_path: Path,
    input_data_path: Path,
    output_file: Path,
) -> config.Config:
    """
    Create a TRoute configuration file with mostly default parameters.

    Parameters
    ==========
    simulation_start : datetime.datetime
      Start date and time of the simulation.
    simulation_end : datetime.datetime
      End date and time of the simulation.
    timestep_in_seconds : int
      Length of the simulation timestep in seconds.
    geopackage_path : Path
      Path to the geospatial file containing the network topology.
    input_data_path : Path
        directory containing simulation forcing data
    output_file : Path
      Path to the output configuration file.

    Returns
    =======
    Config
      The TRoute configuration.
    """

    conf = config.Config(
        log_parameters=__conf_logging(),
        compute_parameters=__conf_compute(
            simulation_start,
            simulation_end,
            timestep_in_seconds,
            input_data_path,
        ),
        network_topology_parameters=__conf_network(
            geopath=types.FilePath(geopackage_path),
        ),
        output_parameters=__conf_output(),
    )

    with open(output_file, "w") as f:
        f.write(to_yaml_str(conf, by_alias=True, exclude_none=True))

    return conf


def __conf_logging() -> logging_parameters.LoggingParameters:
    """
    Create a logging configuration with mostly default parameters.

    Returns
    =======
    logging_parameters.LoggingParameters
        The logging configuration.
    """

    log_conf = logging_parameters.LoggingParameters(log_level="DEBUG", showtiming=True)

    return log_conf


def __conf_network(
    geopath: types.FilePath,
) -> network_topology_parameters.NetworkTopologyParameters:
    """
    Create a network topology configuration with mostly default parameters.

    Parameters
    ==========
    geopath : Path
        Path to the geospatial file containing the network topology.

    Returns
    =======
    network_topology_parameters.NetworkTopologyParameters
        The network topology configuration.
    """

    super_conf = network_topology_parameters.SupernetworkParameters(
        geo_file_path=str(geopath),
        synthetic_wb_segments=None,
        duplicate_wb_segments=None,
    )
    lp = network_topology_parameters.LevelPool(
        level_pool_waterbody_parameter_file_path=geopath
    )

    wb = network_topology_parameters.WaterbodyParameters(
        break_network_at_waterbodies=False, level_pool=lp
    )

    network_conf = network_topology_parameters.NetworkTopologyParameters(
        supernetwork_parameters=super_conf, waterbody_parameters=wb
    )

    return network_conf


def __conf_compute(
    st: datetime.datetime,
    et: datetime.datetime,
    timestep_sec: int = 300,
    input_data_path: Path = Path("./"),
) -> compute_parameters.ComputeParameters:
    """
    Create a compute configuration with mostly default parameters.

    Parameters
    ==========
    st : datetime.datetime
      Start date and time of the simulation.
    et : datetime.datetime
      End date and time of the simulation.
    timestep_sec : int
      Length of the simulation timestep in seconds.
    input_data_path : Path
      directory containing streamflow data that will be routed


    Returns
    =======
    compute_parameters.ComputeParameters
      The compute configuration.
    """

    # compute number of timesteps in the simulation
    nts_per_day = 86400 / timestep_sec
    ndays = (et - st).days
    nts = int(ndays * nts_per_day)

    restart = compute_parameters.RestartParameters(start_datetime=st)

    hybrid = compute_parameters.HybridParameters(run_hybrid_routing=False)

    forcing = compute_parameters.ForcingParameters(
        qts_subdivisions=12,
        dt=timestep_sec,
        nts=nts,
        max_loop_size=720,
        qlat_file_index_col="feature_id",
        qlat_file_value_col="q_lateral",
        qlat_file_gw_bucket_flux_col="qBucket",
        qlat_file_terrain_runoff_col="qSfcLatRunoff",
        qlat_file_pattern_filter="nex-*",
        qlat_input_folder=types.DirectoryPath(input_data_path),
        binary_nexus_file_folder=types.DirectoryPath(input_data_path),
    )

    streamflow_da = compute_parameters.StreamflowDA(
        streamflow_nudging=False, diffusive_streamflow_nudging=False
    )

    reservoir_da = compute_parameters.ReservoirDA(
        reservoir_persistence_da=None,
        reservoir_rfc_da=compute_parameters.ReservoirRfcParameters(),
        reservoir_parameter_file=None,
    )

    da = compute_parameters.DataAssimilationParameters(
        streamflow_da=streamflow_da,
        reservoir_da=reservoir_da,
    )

    comp_conf = compute_parameters.ComputeParameters(
        parallel_compute_method="by-subnetwork-jit-clustered",
        assume_short_ts=True,
        restart_parameters=restart,
        hybrid_parameters=hybrid,
        forcing_parameters=forcing,
        data_assimilation_parameters=da,
    )

    return comp_conf


def __conf_output(
    output_path: types.DirectoryPath = types.DirectoryPath("./"),
) -> output_parameters.OutputParameters:
    """
    Create an output configuration with mostly default parameters.

    Parameters
    ==========
    output_path : Path
      Path to the output directory.

    Returns
    =======
    output_parameters.OutputParameters
      The output configuration.
    """

    csv = output_parameters.CsvOutput(csv_output_folder=output_path)

    out_conf = output_parameters.OutputParameters(csv_output=csv)

    return out_conf
