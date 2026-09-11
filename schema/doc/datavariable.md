# Data Variable and Dimension Metadata

CUAHSI's `schema/src/datavariable.py` module extends the Schema.Org vocabulary with two
classes — `Dimension` and `DataVariable` — used to describe the structure of scientific
data variables (rasters, vectors, multi-dimensional arrays, and tabular data) within a
[`ScientificDataset`](dataset.md#dimensions).

|Concept|What it Describes|Example|Notes|
|---|---|---|---|
|Dimension|Size/extent of an axis|`time = 12`, `lat = 90`|An abstract axis of the dataset.|
|Variable (`variableMeasured`)|The main data array(s)|`temp(time, lat, lon)`|Can be scalar or multi-dimensional; referenced via `variableMeasured`.|
|Coordinate Variable (`coordinates`)|Values that exist along a dimension|`lat(lat)`, `time(time)`|Typically shares its name with the dimension it indexes.|

## Dimension

`"@type": "Dimension"` defines an axis of a variable and provides its shape (size).

|Property|Expected Type|Cardinality|Description|
|---|---|---|---|
|name|Text|1|The name of the dimension.|
|shape|Integer|1|The size/extent of the dimension.|
|description|Text|0,1|A description of the dimension.|

``` json
{
    "@type": "Dimension",
    "name": "feature_index",
    "shape": 18,
    "description": "index of spatial features"
}
```

## DataVariable

`"@type": "DataVariable"` describes a data variable (or coordinate variable), tying it
to one or more named dimensions and, optionally, its data type, unit, and value range.

|Property|Expected Type|Cardinality|Description|
|---|---|---|---|
|name|Text|1|The name of the variable measured.|
|dimensions|Text \| List[Text]|1+|The name(s) of the dimension(s) the variable is defined over.|
|description|Text|0,1|A description of the variable measured.|
|dataType|Text|0,1|The data type of the variable (e.g., `int32`, `float64`, `geometry`).|
|unit|Text|0,1|The unit of the variable measured.|
|minValue|Number \| Text|0,1|The minimum value observed for the variable.|
|maxValue|Number \| Text|0,1|The maximum value observed for the variable.|
|noDataValue|Number \| Text|0,1|The value used to represent null/no-data.|

A `DataVariable` representing a single-dimension numeric field:

``` json
{
    "@type": "DataVariable",
    "name": "HUC_ID",
    "dimensions": "feature_index",
    "dataType": "int64",
    "minValue": 101900030406.0,
    "maxValue": 101900050705.0
}
```

A `DataVariable` representing a multi-dimensional raster/array variable:

``` json
{
    "@type": "DataVariable",
    "name": "elevation",
    "dimensions": ["band", "row", "col"],
    "dataType": "float32",
    "unit": "meters",
    "noDataValue": -9999.0
}
```

A coordinate variable — placed in `coordinates` rather than `variableMeasured` — that
shares its name with the dimension it indexes:

``` json
{
    "@type": "DataVariable",
    "name": "time",
    "dimensions": "time",
    "dataType": "datetime64[ns]"
}
```

## Usage by Data Format

The `schema/notebooks/` directory demonstrates how `Dimension` and `DataVariable` map
onto common scientific data formats when building a [`ScientificDataset`](dataset.md):

|Format Family|Notebook|Dimension Example|Variable Example|
|---|---|---|---|
|Vector (Shapefile, GeoJSON, GML)|`vector.ipynb`|`feature_index = 18`|`geometry(feature_index)`, attribute fields|
|Raster (single/multi-band GeoTIFF, ASCII Raster)|`raster.ipynb`|`row = 12`, `column = 10`, `band = 5`|`elevation(band, row, col)`|
|Multi-dimensional (NetCDF, Zarr)|`multidimensional.ipynb`|`time = 12`, `lat = 90`, `lon = 180`|`temp(time, lat, lon)`, with `time(time)` as a coordinate|
|Tabular (CSV, Parquet, USGS NWIS)|`tabular.ipynb`|`rows = 12`, `columns = 10`|Column values indexed by row|

See `schema/src/dataset.py` for the `AdditionalType` enum (`GeographicFeature`,
`GeographicRaster`, `MultiDimensional`, `Tabular`) used on `ScientificDataset` to
indicate which of these format families a given record represents.
