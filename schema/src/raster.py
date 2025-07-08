#!/usr/bin/env python3

"""
CUAHSI's extension to the SchemaOrg vocabulary to better encapsulate
scientific raster metadata.
"""

from typing import List, Union, Optional, Literal
from pydantic import Field, field_validator, BaseModel, HttpUrl
from .base import PropertyValue, Place
from .dataset import GenericDataset
from .datavariable import BandVariable


class GeographicRaster(GenericDataset):
    """
    Scientific data stored in a raster format. This should support common formats
    sucha as ESRI Grid, ASCII Raster, and GeoTiff.
    """

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )

    type: Literal["GeographicRaster"] = Field(
        alias="@type",  # type: ignore
        default="GeographicRaster",
        description="A body of structured information describing geographic raster information.",
    )

    rows: int = Field(
        title="Raster Rows", description="The number of rows in the raster"
    )
    columns: int = Field(
        title="Raster Columns", description="The number of columns in the raster"
    )
    xCellSize: float = Field(
        title="X Cell Size",
        description="The size of the raster cell in the X direction",
    )
    yCellSize: float = Field(
        title="Y Cell Size",
        description="The size of the raster cell in the Y direction",
    )
    cellValueType: str = Field(
        title="Cell Data Type",
        description="The type of data stored in the raster, e.g. Float32, Int64, etc",
    )
    variableMeasured: List[
        Union[
            str,
            PropertyValue,
            BandVariable,
        ]
    ] = Field(
        title="Variables measured",
        description="The variables that are measured in the raster dataset.",
    )
    spatialCoverage: Place = Field(
        title="Spatial Coverage",
        description="The spatialCoverage indicates the place(s) which are the focus of the content. ",
    )

    @field_validator("cellValueType")
    def validate_content_size(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("empty string")

        if v.upper() not in [
            "BYTE",
            "UINT16",
            "INT16",
            "UINT32",
            "INT32",
            "FLOAT32",
            "FLOAT64",
            "CINT16",
            "CINT32",
            "CFLOAT32",
            "CFLOAT64",
        ]:
            raise ValueError("data type")

        return v
