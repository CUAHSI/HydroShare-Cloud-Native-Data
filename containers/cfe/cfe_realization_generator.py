#!/usr/bin/env python3

import sys
import typing
import pandas
import logging
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

from ngen.config.init_config import cfe as cfe_init
from ngen.config import formulation, cfe, sloth, multi, configurations
from ngen.config.realization import Realization, CatchmentRealization, NgenRealization
from ngen.config.configurations import Forcing, Time, Routing

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def create_global_cfe_realization(
    noah_params_path: Path,
    starttime: datetime,
    endtime: datetime,
    forcing_path: Path,
    output_config_path: Path,
) -> bool:
    """
    Creates a global-level cfe realization.

    Parameters
    ----------
    noah_params_path:  pathlib.Path
        path to noah parameters obtained from the HydroFabric
    start: datetime.datetime
        start date of simulation
    end: datetime.datetime
        end date of simulation
    forcing_path: pathlib.Path
        path to the directory containing forcing files (*.csv)
    output_config_path: pathlib.Path
        path to save the output configuration files

    """

    # create output path if it doesn't exist
    if not output_config_path.exists():
        log.info("creating output directory for configuration files")
        output_config_path.mkdir()

    # read noah parameters
    df_noah_params = pandas.read_csv(noah_params_path)
    catchment_atts = parse_cfe_parameters(df_noah_params)

    # loop through each catchment write ini configs
    log.info("writing catchment config files (*.ini)")
    for cat_id, atts in catchment_atts.items():

        # initialize object that will be used to
        # create catchment-specific ini config files
        cfe_conf = cfe_init.CFEBase(**atts)

        # write ini file
        cfe_conf.Config.no_section_headers = True
        cfe_conf.Config.space_around_delimiters = False
        cfe_conf.Config.preserve_key_case = True
        conf_path = output_config_path / f"{cat_id}_config.ini"
        cfe_conf.to_ini(conf_path)

    # Create the global formulation
    # This is used for any area that is not defined in the catchment realizations.
    # This is unnecessary if every catchment has a catchment-realization,
    # however it's good practice to include this anyway, just in case.
    # In this case, we'll just use the configuration for the first catchment

    # TODO output_interval should be a configurable input
    log.debug("Creating global realization")
    simulation_time = Time(
        start_time=starttime,
        end_time=endtime,
        output_interval=3600,
    )

    # TODO: t_route config path should be a configurable input
    routing = Routing(t_route_config_file_with_path="/ngen/data/config/ngen.yaml")

    # create cfe formulation
    cfe_formulation = create_cfe_formulation(
        conf_path=Path("/ngen/data/config/{{id}}_config.ini"),
        uses_forcing_file=False,
        forcing_file="",
    )

    # create sloth formulation
    sloth_formulation = create_sloth_formulation()

    # wrap cfe and sloth in bmi-multi
    multi_formulation = create_bmi_multi_formulation(
        [sloth_formulation, cfe_formulation]
    )

    # Create catchment realization.
    # This consists of forcing and the multi_formulation combined into
    # a realization. This is cast to a catchment realization and saved
    # to a dictionary for later.
    provider = configurations.Forcing.Provider.CSV
    forcing_configuration = configurations.Forcing(
        file_pattern=".*{{id}}.*.csv",
        path=Path("/ngen/data/forcing/"),
        provider=provider,
    )

    realization = Realization(
        formulations=[multi_formulation], forcing=forcing_configuration
    )

    full_ngen_realization = NgenRealization(
        global_config=realization,
        time=simulation_time,
        catchments=None,
        routing=routing,
        output_root=Path("/ngen/data/results"),
    )
    with open(output_config_path / "realization.json", "w") as f:
        f.write(full_ngen_realization.json(by_alias=True, exclude_none=True, indent=4))
    log.info("Created global realization")

    log.debug("create_default_cfe_realization completed successfully")
    log.debug(f"CFE Init Configs: {output_config_path}/[cat-id]_config.ini")
    log.debug(f'Realization JSON: {output_config_path/"realization.json"}')

    return True


def create_catchment_cfe_realization(
    noah_params_path: Path,
    starttime: datetime,
    endtime: datetime,
    forcing_path: Path,
    output_config_path: Path,
) -> bool:
    """
    Creates a cfe realization consisting of catchment definitions for
    every catchment defined in the noah_params

    Parameters
    ----------
    noah_params_path:  pathlib.Path
        path to noah parameters obtained from the HydroFabric
    start: datetime.datetime
        start date of simulation
    end: datetime.datetime
        end date of simulation
    forcing_path: pathlib.Path
        path to the directory containing forcing files (*.csv)
    output_config_path: pathlib.Path
        path to save the output configuration files

    """

    # create output path if it doesn't exist
    if not output_config_path.exists():
        log.info("creating output directory for configuration files")
        output_config_path.mkdir()

    # read noah parameters
    df_noah_params = pandas.read_csv(noah_params_path)
    catchment_atts = parse_cfe_parameters(df_noah_params)

    # loop through each catchment write ini configs
    log.info("writing catchment config files (*.ini)")
    cfe_confs = []
    catchment_realizations = {}
    for cat_id, atts in catchment_atts.items():

        # initialize object that will be used to
        # create catchment-specific ini config files
        cfe_conf = cfe_init.CFEBase(**atts)

        # write ini file
        cfe_conf.Config.no_section_headers = True
        conf_path = output_config_path / f"{cat_id}_config.ini"
        cfe_conf.to_ini(conf_path)

        # save for later
        cfe_confs.append(cfe_conf)

        # create cfe formulation
        cfe_formulation = create_cfe_formulation(Path(conf_path))

        # create sloth formulation
        sloth_formulation = create_sloth_formulation()

        # wrap cfe and sloth in bmi-multi
        multi_formulation = create_bmi_multi_formulation(
            [sloth_formulation, cfe_formulation]
        )

        # Create catchment realization.
        # This consists of forcing and the multi_formulation combined into
        # a realization. This is cast to a catchment realization and saved
        # to a dictionary for later.
        provider = configurations.Forcing.Provider.CSV
        forcing_configuration = configurations.Forcing(
            path=forcing_path / f"{cat_id}.csv", provider=provider
        )

        realization = Realization(
            formulations=[multi_formulation], forcing=forcing_configuration
        )
        catchment_realizations[cat_id] = CatchmentRealization(
            **realization.dict(by_alias=True)
        )

    # Create the global formulation
    # This is used for any area that is not defined in the catchment realizations.
    # This is unnecessary if every catchment has a catchment-realization,
    # however it's good practice to include this anyway, just in case.
    # In this case, we'll just use the configuration for the first catchment

    # TODO output_interval should be a configurable input
    log.debug("Creating global realization")
    simulation_time = Time(
        start_time=starttime,
        end_time=endtime,
        output_interval=3600,
    )
    # TODO: t_route config path should be a configurable input
    routing = Routing(t_route_config_file_with_path="/ngen/data/config/ngen.yaml")

    first_realization_dict = (
        next(iter(catchment_realizations.values())).copy(deep=True).dict(by_alias=True)
    )
    first_realization_dict["forcing"]["path"] = forcing_path
    first_realization_dict["forcing"]["file_pattern"] = ".*{{id}}.*.csv"
    global_realization = Realization(**first_realization_dict)
    log.info("Created global realization")

    log.debug("Creating global realization")
    full_ngen_realization = NgenRealization(
        global_config=global_realization,
        catchments=catchment_realizations,
        time=simulation_time,
        routing=routing,
    )
    with open(output_config_path / "realization.json", "w") as f:
        f.write(full_ngen_realization.json(by_alias=True, exclude_none=True, indent=4))
    log.info("Created global realization")

    log.debug("create_default_cfe_realization completed successfully")
    log.debug(f"CFE Init Configs: {output_config_path}/[cat-id]_config.ini")
    log.debug(f'Realization JSON: {output_config_path/"realization.json"}')

    return True


def create_bmi_multi_formulation(
    modules: typing.List, main_output_variable: str = "Q_OUT"
) -> formulation.Formulation:

    params = dict(
        name="bmi_multi",
        main_output_variable=main_output_variable,
        init_config="",
        allow_exceed_end_time=True,
        fixed_time_step=False,
        uses_forcing_file=False,
        forcing_file="",
        modules=modules,
    )
    multi_params = multi.MultiBMI(**params)
    dat = {"params": multi_params, "name": multi_params.name}
    multi_formulation = formulation.Formulation(**dat)
    return multi_formulation


def create_sloth_formulation() -> formulation.Formulation:
    sloth_params = dict(
        name="bmi_c++",
        main_output_variable="z",
        init_config="/dev/null",
        allow_exceed_end_time=True,
        fixed_time_step=False,
        uses_forcing_file=False,
        forcing_file="",
        model_params={
            "sloth_ice_fraction_schaake(1,double,m,node)": "0.0",
            "sloth_ice_fraction_xinanjiang(1,double,1,node)": "0.0",
            "sloth_smp(1,double,1,node)": "0.0",
            "EVAPOTRANS": "0.0",
        },
        library_file="/dmod/shared_libs/libslothmodel.so",
    )

    sloth_params = sloth.SLOTH(**sloth_params)
    dat = {"params": sloth_params, "name": sloth_params.name}
    sloth_formulation = formulation.Formulation(**dat)
    return sloth_formulation


def create_cfe_formulation(
    conf_path: Path,
    allow_exceed_time=True,
    fixed_time_step=False,
    uses_forcing_file=True,
    forcing_file="",
) -> formulation.Formulation:
    cfe_params = dict(
        name="bmi_c",
        config=conf_path,
        library_file="/dmod/shared_libs/libcfebmi.so.1.0.0",
        allow_exceed_end_time=allow_exceed_time,
        fixed_time_step=fixed_time_step,
        uses_forcing_file=uses_forcing_file,
        # f"/ngen/data/forcing/{cat_id}",
        forcing_file=forcing_file,
        variables_names_map={
            "atmosphere_water__liquid_equivalent_precipitation_rate": "precip_rate",
            "water_potential_evaporation_flux": "EVAPOTRANS",
            "ice_fraction_schaake": "sloth_ice_fraction_schaake",
            "ice_fraction_xinanjiang": "sloth_ice_fraction_xinanjiang",
            "soil_moisture_profile": "sloth_smp",
        },
    )
    cfe_params = cfe.CFE(**cfe_params)
    dat = {"params": cfe_params, "name": cfe_params.name}
    cfe_formulation = formulation.Formulation(**dat)
    return cfe_formulation


def parse_cfe_parameters(
    cfe_noahowp_attributes: pandas.DataFrame,
) -> typing.Dict[str, dict]:
    """
    Parses parameters from NOAHOWP_CFE DataFrame

    Parameters
    ----------
    cfe_noahowp_attributes: pandas.DataFrame
        Dataframe of NoahOWP CFE parameters

    Returns
    -------
    Dict[str, dict]: parsed CFE parameters

    """
    catchment_configs = {}
    for idx, row in cfe_noahowp_attributes.iterrows():
        d = OrderedDict()

        # static parameters
        d["forcing_file"] = "BMI"
        d["surface_partitioning_scheme"] = "Schaake"

        # ----------------
        # State Parameters
        # ----------------

        # soil depth
        d["soil_params.depth"] = "2.0[m]"

        # many of these values are taken from the 2m depth in hydrofabrics cfe_noahowp_attributes
        d["soil_params.b"] = (
            f'{row["bexp_soil_layers_stag=2"]}[]'  # 	beta exponent on Clapp-Hornberger (1978) soil water relations
        )

        # saturated hydraulic conductivity
        d["soil_params.satdk"] = f'{row["dksat_soil_layers_stag=2"]}[m s-1]'

        # saturated capillary head
        d["soil_params.satpsi"] = f'{row["psisat_soil_layers_stag=2"]}[m]'

        # this factor (0-1) modifies the gradient of the hydraulic head at the soil bottom. 0=no-flow.
        d["soil_params.slop"] = f'{row["slope"]}[m/m]'

        # saturated soil moisture content
        d["soil_params.smcmax"] = f'{row["smcmax_soil_layers_stag=2"]}[m/m]'

        # wilting point soil moisture content
        d["soil_params.wltsmc"] = f'{row["smcwlt_soil_layers_stag=2"]}[m/m]'

        # ---------------------
        # Adjustable Parameters
        # ---------------------

        # optional; defaults to 1.0
        d["soil_params.expon"] = (
            f'{row["gw_Expon"]}[]' if row["gw_Expon"] is not None else "1.0[]"
        )

        # optional; defaults to 1.0
        # not sure if this is the correct key
        d["soil_params.expon_secondary"] = (
            f'{row["gw_Coeff"]}[]' if row["gw_Coeff"] is not None else "1.0[]"
        )

        # maximum storage in the conceptual reservoir
        d["max_gw_storage"] = (
            f'{row["gw_Zmax"]}[m]' if row["gw_Zmax"] is not None else "0.011[m]"
        )

        # primary outlet coefficient
        d["Cgw"] = "0.0018[m h-1]"

        # exponent parameter (1.0 for linear reservoir)
        d["expon"] = "6.0[]"

        # initial condition for groundwater reservoir - it is the ground water as a
        # decimal fraction of the maximum groundwater storage (max_gw_storage) for the initial timestep
        d["gw_storage"] = "0.05[m/m]"

        # field capacity
        d["alpha_fc"] = "0.33[]"

        # initial condition for soil reservoir - it is the water in the soil as a
        # decimal fraction of maximum soil water storage (smcmax * depth) for the initial timestep
        d["soil_storage"] = "0.05[m/m]"

        # number of Nash lf reservoirs (optional, defaults to 2, ignored if storage values present)
        d["K_nash"] = "0.03[]"

        # Nash Config param - primary reservoir
        d["K_lf"] = "0.01[]"

        # Nash Config param - secondary reservoir
        d["nash_storage"] = "0.0,0.0"

        # Giuh ordinates in dt time steps
        d["giuh_ordinates"] = "1.00,0.00"

        # ---------------------
        # Time Info
        # ---------------------

        # set to 1 if forcing_file=BMI
        d["num_timesteps"] = "1"

        # ---------------------
        # Options
        # ---------------------

        # prints various debug and bmi info
        d["verbosity"] = "0"

        d["DEBUG"] = "0"

        # Parameter in the surface runoff parameterization
        # (https://mikejohnson51.github.io/hyAggregate/#Routing_Attributes)
        d["refkdt"] = f'{row["refkdt"]}'

        catchment_configs[row.divide_id] = d

    return catchment_configs


if __name__ == "__main__":
    noah_params_path = Path("test-data/domain/cfe_noahowp_attributes.csv")
    forcing_path = Path("extra/old stuff/working-example/forcings")
    output_config_path = Path("output-data/config")

    # noah_params_csv: Path,
    # start: datetime,
    # end: datetime,
    # forcing_path: Path,
    # output_config_path: Path) -> str:
    create_catchment_cfe_realization(
        noah_params_path,
        datetime(2020, 1, 1),
        datetime(2021, 1, 1),
        forcing_path,
        output_config_path,
    )
