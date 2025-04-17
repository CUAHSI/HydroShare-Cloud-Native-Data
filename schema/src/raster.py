from typing import List, Union, Optional, Literal
from pydantic import Field, field_validator, BaseModel, HttpUrl
from base import PropertyValue


from dataset import GenericDataset

# TODO: How well does this align with the HS_MODELS representation that Scott shared?


class GridVariable(BaseModel):

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )
    type: Literal["GridVariable"] = Field(
        alias="@type",  # type: ignore
        default="GridVariable",
        description="A body of structured information describing geographic raster information.",
    )

    # required fields
    minValue: float = Field(
        title="Minimum Value", description="The ,inimum value in the raster grid"
    )
    maxValue: float = Field(
        title="Maximum Value", description="The maximum value in the raster grid"
    )
    noDataValue: float = Field(
        title="No Data Value",
        description="The numerical value used to represent null data in the raster grid",
    )

    # optional fields
    name: Optional[str] = Field(
        default=None,
        title="Variable Name",
        description="The name of the variable measured in grid",
    )
    variableMeasured: Optional[Union[str, PropertyValue]] = Field(
        default=None,
        title="Variables measured",
        description="A description of the variable that is measured in the raster grid.",
    )
    band: Optional[Union[str, int]] = Field(
        default=None,
        title="Raster Band",
        description="The band number or identifier for the variable measured in the raster grid.",
    )


class GeographicRaster(GenericDataset):
    """
    Scientific data stored in a raster format. This should support common formats
    sucha as ESRI Grid, ASCII Raster, and GeoTiff.
    """

    # TODO: SpatialExtent should be required.

    # context: HttpUrl = Field(
    #     alias="@context",  # type: ignore
    #     default=HttpUrl("https://schema.org"),
    #     description="Specifies the vocabulary employed for understanding the structured data markup.",
    # )
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
    variableMeasured: List[Union[str, PropertyValue, GridVariable]] = Field(
        title="Variables measured",
        description="The variables that are measured in the raster dataset.",
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
