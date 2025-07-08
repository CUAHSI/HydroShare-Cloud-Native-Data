#!/usr/bin/env python3

"""
CUAHSI's extension to the SchemaOrg vocabulary to better encapsulate
multi-dimensional scientific metadata.
"""

from typing import List, Union, Optional, Literal
from pydantic import Field, field_validator, BaseModel, HttpUrl
from base import PropertyValue, Place


from dataset import GenericDataset
from datavariable import DataVariable, Dimension

# array
# matrix
# cube

class MultiDimensional(GenericDataset):
    """
    Scientific data stored in a MultiDimensional format. This should support common formats
    such as NetCDF, HDF5, and Zarr.
    """

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )

    type: Literal["MultiDimensional"] = Field(
        alias="@type",  # type: ignore
        default="MultiDimensional",
        description="A body of structured information describing MultiDimensional information.",
    )

    variableMeasured: List[DataVariable] = Field(
        title="Variables measured",
        description="The variables that are measured in the raster dataset.",
    )

    coordinates: List[DataVariable] = Field(
        title="Coordinates",
        description="Coordinate variables that provide values along a dimension",
    )

    dimensions: List[Dimension] = Field(
        title="Dimensions",
        description="Dimensions defined in the multi-dimensional dataset.",
    )
