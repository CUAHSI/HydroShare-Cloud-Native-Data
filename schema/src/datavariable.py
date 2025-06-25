#!/usr/bin/env python3

"""
CUAHSI's extension to the SchemaOrg vocabulary to better encapsulate
scientific data variable metadata.
"""

from typing import Optional, Literal, Union
from pydantic import Field, BaseModel, HttpUrl


class Dimension(BaseModel):
    """
    A variable dimension defines an axes of a variable; it provides the shape of the variable.

    """

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )
    type: Literal["Dimension"] = Field(
        alias="@type",  # type: ignore
        default="Dimension",
        description="A body of structured information describing variable dimensions.",
    )
    name: str = Field(
        title="Dimension Name",
        description="The name of the dimension",
    )
    shape: int = Field(
        title="Variable Shape",
        description="The shape of the variable",
    )
    description: Optional[str] = Field(
        default=None,
        title="Variable Description",
        description="The description of the variable measured",
    )

class DataVariable(BaseModel):

    context: HttpUrl = Field(
        alias="@context",  # type: ignore
        default=HttpUrl(
            "https://hydroshare.org/schema"
        ),  # TODO: This is a placeholder for now.
        description="Specifies the vocabulary employed for understanding the structured data markup.",
    )
    type: Literal["DataVariable"] = Field(
        alias="@type",  # type: ignore
        default="DataVariable",
        description="A body of structured information describing core metadata shared by all data variables.",
    )

    name: str = Field(
        title="Variable Name",
        description="The name of the variable measured",
    )

    # dimension: Union[Dimension, list[Dimension]] = Field(
    #     title="Variable Dimensions",
    #     description="The dimensions of the variable measured",
    # )
    dimensions: Union[str, list[str]] = Field(
        title="Variable Dimensions",
        description="The dimension names corresponding to the variable being measured",
    )
    
    # coordinates: Optional[Union[DataVariable, list[DataVariable]]] = Field(
    #     title="Coordinates",
    #     description="Coordinate variables that provide values along a dimension",
    # )
    description: Optional[str] = Field(
        default=None,
        title="Variable Description",
        description="The description of the variable measured",
    )
    dataType: Optional[str] = Field(
        default=None,
        title="The data type of the variable",
        description="The data type of the variable measured",
    )
    unit: Optional[str] = Field(
        default=None,
        title="Variable Unit",
        description="The unit of the variable measured",
    )
    # shape: Optional[Union[int, list[int]]] = Field(
    #     default=None,
    #     title="Variable Shape",
    #     description="The shape of the variable",
    # )
    minValue: Optional[float] = Field(
        title="Minimum Value",
        description="The minimum value in the raster grid",
        default=None,
    )
    maxValue: Optional[float] = Field(
        title="Maximum Value",
        description="The maximum value in the raster grid",
        default=None,
    )
    noDataValue: Optional[float] = Field(
        title="No Data Value",
        description="The numerical value used to represent null data in the raster grid",
        default=None,
    )


# TODO: Coordinate should be defined in the multidimensional class
# with a type of datavariable. This is because it is really just a
# special type of datavariable.
#
# class Coordinate(DataVariable):
#    """
#    A coordinate provides meaning to dimensions by providing physical values (e.g. degrees, meters, timestamps, etc)
#    for abstract dimension indices. It is a special type of variable.
#    """
#
#    context: HttpUrl = Field(
#        alias="@context",  # type: ignore
#        default=HttpUrl(
#            "https://hydroshare.org/schema"
#        ),  # TODO: This is a placeholder for now.
#        description="Specifies the vocabulary employed for understanding the structured data markup.",
#    )
#    type: Literal["Coordinate"] = Field(
#        alias="@type",  # type: ignore
#        default="Coordinate",
#        description="A body of structured information describing variable coordinates.",
#    )


# class GriddedVariable(DataVariable):

#     context: HttpUrl = Field(
#         alias="@context",  # type: ignore
#         default=HttpUrl(
#             "https://hydroshare.org/schema"
#         ),  # TODO: This is a placeholder for now.
#         description="Specifies the vocabulary employed for understanding the structured data markup.",
#     )
#     type: Literal["GriddedVariable"] = Field(
#         alias="@type",  # type: ignore
#         default="GriddedVariable",
#         description="A body of structured information describing gridded variable information.",
#     )

#     # required fields
#     dataType: str = Field(
#         title="The data type of the variable",
#         description="The data type of the variable measured",
#     )


#     # optional fields
#     name: Optional[str] = Field(
#         default=None,
#         title="Variable Name",
#         description="The name of the variable measured in grid",
#     )
#     minValue: Optional[float] = Field(
#         title="Minimum Value", description="The minimum value in the grid"
#     )
#     maxValue: Optional[float] = Field(
#         title="Maximum Value", description="The maximum value in the grid"
#     )
#     noDataValue: Optional[float] = Field(
#         title="No Data Value",
#         description="The numerical value used to represent null data in the grid",
#     )
    


# class BandVariable(GriddedVariable):

#     context: HttpUrl = Field(
#         alias="@context",  # type: ignore
#         default=HttpUrl(
#             "https://hydroshare.org/schema"
#         ),  # TODO: This is a placeholder for now.
#         description="Specifies the vocabulary employed for understanding the structured data markup.",
#     )
#     type: Literal["BandVariable"] = Field(
#         alias="@type",  # type: ignore
#         default="BandVariable",
#         description="A body of structured information describing gridded band information.",
#     )

#     # required fields
#     band: Union[str, int] = Field(
#         title="Raster Band",
#         description="The band number or identifier for the variable measured in the raster grid.",
#     )
#     # dataType: str = Field(
#     #     title="The data type of the variable",
#     #     description="The data type of the variable measured",
#     # )
#     # minValue: float = Field(
#     #     title="Minimum Value",
#     #     description="The minimum value in the raster grid",
#     # )
#     # maxValue: float = Field(
#     #     title="Maximum Value",
#     #     description="The maximum value in the raster grid",
#     # )
#     # noDataValue: float = Field(
#     #     title="No Data Value",
#     #     description="The numerical value used to represent null data in the raster grid",
#     # )
#     # # optional fields
#     # name: Optional[str] = Field(
#     #     default=None,
#     #     title="Variable Name",
#     #     description="The name of the variable measured in grid",
#     # )
#     #     coordinates: List[DataVariable] = Field(
#     #     title="Coordinates",
#     #     description="Coordinate variables that provide values along a dimension",
#     # )
