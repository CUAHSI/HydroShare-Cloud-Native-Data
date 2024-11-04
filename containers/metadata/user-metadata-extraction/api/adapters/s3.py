import json
from http import HTTPStatus

import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError as S3ClientError

from api.adapters.base import AbstractRepositoryMetadataAdapter, AbstractRepositoryRequestHandler
from api.adapters.utils import RepositoryType, register_adapter
from api.exceptions import RepositoryException
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission


class _S3RequestHandler(AbstractRepositoryRequestHandler):
    def get_metadata(self, record_id: str):
        endpoint_url = record_id.split("+")[0]
        bucket_name = record_id.split("+")[1]
        file_key = record_id.split("+")[2]

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED), endpoint_url=endpoint_url)
        try:
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
        except S3ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                raise RepositoryException(
                    detail=f"Specified metadata file was not found in S3: {bucket_name}/{file_key}",
                    status_code=HTTPStatus.NOT_FOUND
                )
            else:
                err_msg = f"Error accessing S3 file({bucket_name}/{file_key}): {str(ex)}"
                raise RepositoryException(detail=err_msg, status_code=HTTPStatus.BAD_REQUEST)

        json_content = response['Body'].read().decode('utf-8')
        # Parse the JSON content
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as ex:
            err_msg = f"Invalid JSON content in S3 file ({file_key}). Error: {str(ex)}"
            raise RepositoryException(detail=err_msg, status_code=HTTPStatus.BAD_REQUEST)

        return data


class S3MetadataAdapter(AbstractRepositoryMetadataAdapter):
    repo_api_handler = _S3RequestHandler()

    @staticmethod
    def to_catalog_record(metadata: dict) -> DatasetMetadataDOC:
        return DatasetMetadataDOC(**metadata)

    @staticmethod
    def to_repository_record(catalog_record: DatasetMetadataDOC):
        """Converts dataset catalog record to hydroshare resource metadata"""
        raise NotImplementedError

    @staticmethod
    def update_submission(submission: Submission, repo_record_id: str) -> Submission:
        """Sets additional hydroshare specific metadata to submission record"""

        submission.repository_identifier = repo_record_id
        submission.repository = RepositoryType.S3
        return submission


register_adapter(RepositoryType.S3, S3MetadataAdapter)
