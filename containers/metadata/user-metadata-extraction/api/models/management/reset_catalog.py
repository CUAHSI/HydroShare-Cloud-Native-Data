import asyncio
import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC

logger = logging.getLogger()


async def main():
    logger.info("Resetting catalog")
    settings = get_settings()
    db_client = AsyncIOMotorClient(settings.db_connection_string)
    db = db_client[get_settings().database_name]
    await init_beanie(database=db, document_models=[DatasetMetadataDOC])

    await db["discovery"].delete_many({})
    logger.info("Deleted all documents in discovery collection")
    print("Deleted all documents in discovery collection")

    # replace all documents in catalog collection to trigger repopulating of discovery collection
    count = 0
    async for catalog_document in DatasetMetadataDOC.find_all():
        await catalog_document.replace()
        count += 1
        print(f"Replaced {count} documents in catalog collection")

    logger.info(f"Replaced all in catalog collection")
    print(f"Replaced all {count} documents in catalog collection")

    db_client.close()


if __name__ == "__main__":
    logger.info("Running reset_catalog.py")
    asyncio.run(main())
