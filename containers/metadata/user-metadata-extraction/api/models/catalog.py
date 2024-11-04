import datetime
from typing import Optional

from beanie import Document

from api.models.user import Submission, S3Path
from .schema import CoreMetadata, DatasetMetadata


class CoreMetadataDOC(Document, CoreMetadata):
    # this field is not stored in the database, but is populated from the corresponding submission record
    # using the type field in the submission record
    submission_type: str = None

    class Settings:
        # name is the collection name in database (iguide) where the Metadata Record documents will be stored
        # for all metadata record types (e.g. dataset, geopackage, software etc.)
        name = "catalog"
        is_root = True
        bson_encoders = {
            datetime.date: lambda dt: datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, second=0
            ),
            datetime.datetime: lambda dt: datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second
            )
        }

    def as_submission(self) -> Submission:
        return Submission(
            title=self.name,
            authors=[creator.name for creator in self.creator],
            submitted=datetime.datetime.utcnow(),
            identifier=self.id,
            url=self.url,
        )


class DatasetMetadataDOC(CoreMetadataDOC, DatasetMetadata):
    repository_identifier: str = None
    s3_path: Optional[S3Path] = None
