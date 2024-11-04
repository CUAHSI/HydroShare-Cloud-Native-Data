from enum import Enum
from typing import Type, Union

from api.adapters.base import AbstractRepositoryMetadataAdapter


class RepositoryType(str, Enum):
    HYDROSHARE = 'HYDROSHARE'
    S3 = 'S3'


_adapter_registry = {}


def register_adapter(repository_type: RepositoryType, adapter_class: Type[AbstractRepositoryMetadataAdapter]) -> None:
    _adapter_registry[repository_type] = adapter_class


def get_adapter_by_type(repository_type: RepositoryType) -> Union[AbstractRepositoryMetadataAdapter, None]:
    adapter_cls = _adapter_registry.get(repository_type, None)
    if adapter_cls:
        return adapter_cls()
    return None
