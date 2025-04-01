from core import CoreMetadata
from typing import Optional, List, Union
from pydantic import Field

from base import PropertyValue, SourceOrganization


class DatasetMetadata(CoreMetadata):
    variableMeasured: Optional[List[Union[str, PropertyValue]]] = Field(
        title="Variables measured", description="Measured variables."
    )
    additionalProperty: Optional[List[PropertyValue]] = Field(
        title="Additional properties",
        default=[],
        description="Additional properties of the dataset.",
    )
    sourceOrganization: Optional[SourceOrganization] = Field(
        title="Source organization",
        description="The organization that provided the data for this dataset.",
    )
