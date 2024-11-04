from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from beanie import Document, Link, PydanticObjectId
from pydantic import HttpUrl, BaseModel

if TYPE_CHECKING:
    # this avoids circular imports
    from api.adapters.utils import RepositoryType


class SubmissionType(str, Enum):
    HYDROSHARE = 'HYDROSHARE'
    S3 = 'S3'
    IGUIDE_FORM = 'IGUIDE_FORM'


class StorageProvider(str, Enum):
    AWS = "AWS"
    GCP = "GCP"
    Azure = "Azure"
    GoogleDrive = "Google Drive"
    Dropbox = "Dropbox"
    OneDrive = "OneDrive"
    Box = "Box"
    CUAHSI = "CUAHSI"


@dataclass
class ContentStorage:
    url_pattern: str
    storage_name: str

    @classmethod
    def get_storage(cls, storage_provider: StorageProvider):
        if storage_provider == StorageProvider.AWS:
            return cls("amazonaws.com", "AWS")

        if storage_provider == StorageProvider.GCP:
            return cls("storage.googleapis.com", "GCP")

        if storage_provider == StorageProvider.Azure:
            return cls("blob.core.windows.net", "Azure")

        if storage_provider == StorageProvider.GoogleDrive:
            return cls("drive.google.com", "Google Drive")

        if storage_provider == StorageProvider.Dropbox:
            return cls("dropbox.com", "Dropbox")

        if storage_provider == StorageProvider.OneDrive:
            return cls("onedrive.live.com", "OneDrive")

        if storage_provider == StorageProvider.Box:
            return cls("app.box.com", "Box")

        if storage_provider == StorageProvider.CUAHSI:
            return cls("minio.cuahsi.io", "CUAHSI")

    def get_storage_name(self, url: Optional[str], repository_identifier: Optional[str]):
        if repository_identifier and self.url_pattern in repository_identifier:
            return self.storage_name
        if url and self.url_pattern in url:
            return self.storage_name
        return None


class S3Path(BaseModel):
    path: str
    bucket: str
    endpoint_url: HttpUrl = 'https://api.minio.cuahsi.io'

    @property
    def identifier(self):
        endpoint_url = self.endpoint_url.rstrip("/")
        identifier = f"{endpoint_url}/{self.bucket}/{self.path}"
        return identifier

    @property
    def fetch_identifier(self):
        # This is the identifier that is used to fetch the file from S3
        return f"{self.endpoint_url}+{self.bucket}+{self.path}"


class Submission(Document):
    title: str = None
    authors: List[str] = []
    identifier: PydanticObjectId
    submitted: datetime = datetime.utcnow()
    url: HttpUrl = None
    repository: Optional[str]
    repository_identifier: Optional[str]
    s3_path: Optional[S3Path]

    @property
    def content_location(self):
        # determine the content location based on the repository type
        if self.repository == SubmissionType.HYDROSHARE:
            return self.repository
        elif self.repository == SubmissionType.S3:
            endpoint_url = self.s3_path.endpoint_url.rstrip("/")
            storage = ContentStorage.get_storage(StorageProvider.AWS)
            if endpoint_url.endswith(storage.url_pattern):
                return storage.storage_name
            storage = ContentStorage.get_storage(StorageProvider.CUAHSI)
            if endpoint_url.endswith(storage.url_pattern):
                return storage.storage_name
            return self.repository

        # determine the content location based on the URL or repository identifier

        # check for GCP
        storage = ContentStorage.get_storage(StorageProvider.GCP)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        # check for Azure
        storage = ContentStorage.get_storage(StorageProvider.Azure)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        # check for Google Drive
        storage = ContentStorage.get_storage(StorageProvider.GoogleDrive)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        # check for dropbox
        storage = ContentStorage.get_storage(StorageProvider.Dropbox)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        # check for one drive
        storage = ContentStorage.get_storage(StorageProvider.OneDrive)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        # check for box
        storage = ContentStorage.get_storage(StorageProvider.Box)
        storage_name = storage.get_storage_name(self.url, self.repository_identifier)
        if storage_name:
            return storage_name

        return self.repository


class User(Document):
    access_token: str
    orcid: str
    preferred_username: Optional[str]
    submissions: List[Link[Submission]] = []

    def submission(self, identifier: PydanticObjectId) -> Submission:
        return next(filter(lambda submission: submission.identifier == identifier, self.submissions), None)

    def submission_by_repository(self, repo_type: 'RepositoryType', identifier: str) -> Submission:
        return next(
            filter(
                lambda submission: submission.repository_identifier == identifier
                and submission.repository == repo_type,
                self.submissions,
            ),
            None,
        )
