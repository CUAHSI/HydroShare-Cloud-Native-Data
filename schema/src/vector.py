#!/usr/bin/env python3

"""
CUAHSI's extension to the SchemaOrg vocabulary to better encapsulate
scientific vector metadata.
"""


from typing import List, Union, Literal, Optional
from pydantic import Field, field_validator, HttpUrl, ConfigDict
from .base import PropertyValue, MediaType, Place, SchemaBaseModel

from .dataset import GenericDataset




class FieldInformation(SchemaBaseModel):
    """
    A class used to represent the metadata associated with a field in the attribute table for a geographic
    feature aggregation
    """

    model_config = ConfigDict(title='Geographic Feature Field Metadata')

    field_name: str = Field(
        max_length=128, title="Field name", description="A string containing the name of the attribute table field",
    )
    field_type: str = Field(
        max_length=128, title="Field type", description="A string containing the data type of the values in the field",
    )
    # TODO: What is the "field_type_code"? It's not displayed on the resource landing page, but it's encoded in the
    #  aggregation metadata as an integer value.
    field_type_code: Optional[str] = Field(
        default=None,
        max_length=50,
        title="Field type code",
        description="A string value containing a code that indicates the field type",
    )
    field_width: Optional[int] = Field(
        default=None, title="Field width", description="An integer value containing the width of the attribute field",
    )
    field_precision: Optional[int] = Field(
        default=None,
        title="Field precision",
        description="An integer value containing the precision of the attribute field",
    )


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

    field_information: List[FieldInformation] = Field(
        default=[],
        title="Field information",
        description="A list of objects containing information about the fields in the dataset attribute table",
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
