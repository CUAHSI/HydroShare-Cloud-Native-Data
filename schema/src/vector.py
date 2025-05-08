#!/usr/bin/env python3

"""
CUAHSI's extension to the SchemaOrg vocabulary to better encapsulate
scientific vector metadata.
"""


from typing import List, Union, Literal
from pydantic import Field, field_validator, HttpUrl
from .base import PropertyValue, MediaType, Place

from .dataset import GenericDataset


class GeographicVector(GenericDataset):
    """
    Scientific data stored in a vector format. This should support common formats
    sucha as ESRI Shapefile, GeoJSON, and GML.
    """

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )
    type: Literal["GeographicVector"] = Field(
        alias="@type",  # type: ignore
        default="GeographicVector",
        description="A body of structured information describing geographic vector information.",
    )

    associatedMedia: Union[MediaType, List[MediaType]] = Field(
        title="Resource content",
        description="A media object that encodes the vector data",
    )

    featureCount: int = Field(
        title="Feature Count",
        description="The number of features in the GeographicVector",
    )
    fieldCount: int = Field(
        title="Field Count",
        description="The number of attribute fields in the GeographicVector",
    )
    geometryType: str = Field(
        title="Geometry Type",
        description="The type of geometry represented in the GeographicVector",
    )
    variableMeasured: List[Union[str, PropertyValue]] = Field(
        title="Variables measured",
        description="The variables that are measured in the GeographicVector dataset.",
    )

    spatialCoverage: Place = Field(
        title="Spatial Coverage",
        description="The spatialCoverage indicates the place(s) which are the focus of the content. ",
    )

    @field_validator("associatedMedia")
    def validate_associated_media(cls, vals):
        if type(vals) is MediaType:
            vals = list(vals)

        input_file_extensions = [v.name.split(".")[-1] for v in vals]

        # if a shapefile is provided, make sure the accompanying files also exist.
        # Shapefiles must contain the following files:
        #   .shp: Shape format – Stores the geometry (points, lines, polygons).
        #   .shx: Shape index – Provides a spatial index for faster access to features.
        #   .dbf: Attribute table – Stores feature attributes in dBASE format.
        if "shp" in input_file_extensions:
            required_shp_extensions = ["shp", "shx", "dbf"]
            if not all(
                req_ext in input_file_extensions for req_ext in required_shp_extensions
            ):
                raise ValueError("Shapefile is missing a required file type")

        return vals
