import asyncio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC


async def main():
    db = AsyncIOMotorClient(get_settings().db_connection_string)
    await init_beanie(database=db[get_settings().database_name], document_models=[DatasetMetadataDOC])
    # https://www.mongodb.com/docs/manual/reference/command/collMod/#change-streams-with-document-pre--and-post-images
    # This enables us to get the record id of a deleted submission within a trigger.  We need this for removing
    # discovery records when a submission is deleted
    await db[get_settings().database_name].command(
        ({'collMod': DatasetMetadataDOC.get_collection_name(), "changeStreamPreAndPostImages": {'enabled': True}}))
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
