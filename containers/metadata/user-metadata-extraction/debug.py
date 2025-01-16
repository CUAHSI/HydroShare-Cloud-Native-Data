from api.adapters import hydroshare as hsadapter
import json


async def run():
    identifier = "8e944afdd73d4cce945c3382bfcd25d9"

    print("Initializing hsadapter")
    adapter = hsadapter.HydroshareMetadataAdapter()

    print("Getting metadata for resource with identifier: {}".format(identifier))
    metadata = await adapter.get_metadata(identifier)

    print("Casting metadata into Pydantic model")
    hs_metadata_model = hsadapter._HydroshareResourceMetadata(**metadata)

    print("Convert Pydantic model into catalog dataset")
    hs_metadata = hs_metadata_model.to_catalog_dataset()

    print("Printing metadata\n---------------------")
    print(hs_metadata.model_dump_json(indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
