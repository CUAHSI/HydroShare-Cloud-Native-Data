#!/usr/bin/env python3

import typer
from pathlib import Path
from asyncio import run as aiorun
from api.adapters import hydroshare as hsadapter

import logging

# Configure the logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()


def main(
    resid: str = typer.Argument(..., help="HydroShare resource id to process"),
    outdir: Path = typer.Argument(Path("."), help="Directory to save output"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print logs to console"
    ),
):

    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    aiorun(extract_metadata(resid, outdir))


async def extract_metadata(resid: str, outdir: Path) -> None:
    """
    This function extracts user and science metadata from a HydroShare resource.
    """

    # -----------------
    # GET USER METADATA
    # -----------------

    # Query user metadata from HydroShare
    logger.info("Initializing hsadapter")
    adapter = hsadapter.HydroshareMetadataAdapter()

    logger.info("Getting metadata for resource with identifier: {}".format(resid))
    metadata = await adapter.get_metadata(resid)

    # get the metadata as pydantic classes
    logger.info("Casting metadata into Pydantic model")
    hs_metadata_model = hsadapter._HydroshareResourceMetadata(**metadata)
    logger.info("Convert Pydantic model into catalog dataset")
    hs_metadata = hs_metadata_model.to_catalog_dataset()

    # write user metadata to file
    logger.info("Writing metadata to file")
    metadata_path = outdir / resid / "data/contents/"
    metadata_path.mkdir(parents=True, exist_ok=True)
    user_metadata = metadata_path / "user_metadata.json"
    with open(user_metadata, "w") as f:
        f.write(hs_metadata.model_dump_json(indent=4))

    logger.info("Printing metadata\n---------------------")
    logger.info(hs_metadata.model_dump_json(indent=4))


if __name__ == "__main__":
    typer.run(main)
