# Example Implementations

This document walks through worked examples of encoding real scientific data files as
[`ScientificDataset`](dataset.md) records, one per data type family. Each example
describes how the source file's structure maps onto `dimensions`, `variableMeasured`,
and `coordinates`, and shows the resulting JSON-LD. The full extraction code, sample
input data, and complete output for each example live in the corresponding Jupyter
notebook under [`schema/notebooks/`](../notebooks) — open the notebook to see the
implementation in Python.

|Data Type|Notebook|`additionalType`|
|---|---|---|
|[Vector](#vector-data)|[`vector.ipynb`](../notebooks/vector.ipynb)|`GeographicFeature`|
|[Raster](#raster-data)|[`raster.ipynb`](../notebooks/raster.ipynb)|`GeographicRaster`|
|[Multi-Dimensional](#multi-dimensional-data)|[`multidimensional.ipynb`](../notebooks/multidimensional.ipynb)|`MultiDimensional`|
|[Tabular](#tabular-data)|[`tabular.ipynb`](../notebooks/tabular.ipynb)|`Tabular`|
|[Spatial Reference System](#spatial-reference-system)|[`spatial-reference-system.ipynb`](../notebooks/spatial-reference-system.ipynb)|n/a (used within `spatialCoverage`)|
|[Data Variable Concepts](#data-variable-concepts)|[`datavariable.ipynb`](../notebooks/datavariable.ipynb)|n/a|

## Vector Data

[`vector.ipynb`](../notebooks/vector.ipynb) demonstrates encoding **Shapefile**,
**GeoJSON**, and **GML** vector files. A vector file has one dimension — the feature
index — and every attribute field (including the geometry column) is a variable over
that dimension.

|File Structure|Maps To|Notes|
|---|---|---|
|Number of features in the file|`dimensions[0]` (`Dimension`, name `feature_index`)|`shape` is set to the feature count.|
|Each attribute column (including `geometry`)|An entry in `variableMeasured` (`DataVariable`)|`dimensions` is set to `feature_index`; `dataType`, `minValue`, `maxValue` are read from the column when numeric.|
|File bounding box and CRS|`spatialCoverage`|Encoded as a `Place` with a `GeoShape` (bounding box) and `SpatialReference` (CRS). See [Spatial Reference System](#spatial-reference-system).|
|Source file(s) (`.shp`, `.shx`, `.dbf`, `.prj`, etc.)|`associatedMedia`|One `MediaObject` per associated file.|

Resulting JSON-LD for a Shapefile (`data/watershed.shp`), abbreviated to two
attribute fields — see the notebook for the complete output including every
attribute:

``` json
{
    "@context": "https://hydroshare.org/schema",
    "@type": "ScientificDataset",
    "additionalType": "GeographicFeature",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": "39.847270779 -105.700627563 40.158935262 -104.933629104"
        },
        "srs": {
            "@type": "SpatialReference",
            "name": "WGS 84",
            "srsType": "geographic",
            "code": "EPSG:4326"
        }
    },
    "associatedMedia": [
        {
            "@type": "MediaObject",
            "name": "watershed.shp",
            "contentUrl": "https://hydroshare.org/my-resource/data/watershed.shp",
            "encodingFormat": "application/x-esri-shapefile",
            "contentSize": "269.75 KB",
            "sha256": "9baf1e4e4e5b1e4946714bf4c153a618791c4e0de006bfa84769fcb1cbaddfe8"
        }
    ],
    "variableMeasured": [
        {
            "@type": "DataVariable",
            "name": "ID",
            "dimensions": "feature_index",
            "dataType": "int32",
            "minValue": 1.0,
            "maxValue": 18.0
        },
        {
            "@type": "DataVariable",
            "name": "geometry",
            "dimensions": "feature_index",
            "dataType": "geometry"
        }
    ],
    "dimensions": [
        {
            "@type": "Dimension",
            "name": "feature_index",
            "shape": 18,
            "description": "index of spatial features"
        }
    ]
}
```

## Raster Data

[`raster.ipynb`](../notebooks/raster.ipynb) demonstrates encoding **single-band
GeoTIFF**, **multi-band GeoTIFF**, and **ASCII Raster** files. A raster's grid extent
becomes `row`/`column` dimensions (plus a `band` dimension for multi-band rasters),
and each band becomes a variable over those dimensions.

|File Structure|Maps To|Notes|
|---|---|---|
|Grid width/height|`dimensions` entries named `columns` and `rows`|`shape` is set to the pixel width/height.|
|Band count (multi-band only)|An additional `band` dimension|Only present when `multiband=True`.|
|Each raster band|An entry in `variableMeasured` (`DataVariable`)|`dimensions` is `["columns", "rows"]`, or `["band", "columns", "rows"]` for multi-band; `minValue`/`maxValue`/`noDataValue` are computed from the pixel data.|
|Raster extent and CRS|`spatialCoverage`|Same `Place`/`GeoShape`/`SpatialReference` pattern as vector data.|
|Source file(s) (`.tif`, `.vrt`, `.prj`, etc.)|`associatedMedia`|One `MediaObject` per associated file.|

Resulting JSON-LD for a single-band GeoTIFF (`data/Onion3ad8o.tif`), abbreviated:

``` json
{
    "@context": "https://hydroshare.org/schema",
    "@type": "ScientificDataset",
    "additionalType": "GeographicRaster",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": "30.014629629 -98.307685185 30.270277778 -97.579537033"
        },
        "srs": {
            "@type": "SpatialReference",
            "name": "NAD83",
            "srsType": "geographic"
        }
    },
    "associatedMedia": [
        {
            "@type": "MediaObject",
            "name": "Onion3ad8o.tif",
            "contentUrl": "https://hydroshare.org/my-resource/data/Onion3ad8o.tif",
            "encodingFormat": "image/tiff",
            "contentSize": "1665.64 KB",
            "sha256": "6ee7ffeaad112ad13e6..."
        }
    ],
    "variableMeasured": [
        {
            "@type": "DataVariable",
            "name": "Band 1",
            "dimensions": [
                "columns",
                "rows"
            ],
            "dataType": "float32",
            "minValue": 0.0,
            "maxValue": 255.0,
            "noDataValue": -9999.0
        }
    ],
    "dimensions": [
        {
            "@type": "Dimension",
            "name": "columns",
            "shape": 1500
        },
        {
            "@type": "Dimension",
            "name": "rows",
            "shape": 1000
        }
    ]
}
```

For a multi-band GeoTIFF, a `band` dimension is added, and each band's
`DataVariable.dimensions` becomes `["band", "columns", "rows"]`:

``` json
{
    "dimensions": [
        {
            "@type": "Dimension",
            "name": "band",
            "shape": 3
        },
        {
            "@type": "Dimension",
            "name": "columns",
            "shape": 800
        },
        {
            "@type": "Dimension",
            "name": "rows",
            "shape": 600
        }
    ]
}
```

## Multi-Dimensional Data

[`multidimensional.ipynb`](../notebooks/multidimensional.ipynb) demonstrates encoding
**NetCDF** files (local) and **Zarr** stores (remote, on cloud object storage). Unlike
vector/raster data, a multi-dimensional dataset distinguishes primary data variables
from coordinate variables that index a dimension by name.

|File Structure|Maps To|Notes|
|---|---|---|
|Each named axis in the array (e.g., `time`, `lat`, `lon`)|An entry in `dimensions` (`Dimension`)|`shape` is the axis length; `description` comes from the `long_name` attribute, if present.|
|Each non-coordinate data array (e.g., `IVT`, `temp`)|An entry in `variableMeasured` (`DataVariable`)|`dimensions` lists every axis the array varies over; `unit`, `description`, `minValue`/`maxValue` are read from array attributes/values.|
|Each coordinate array whose name matches a dimension (e.g., `time(time)`, `lat(lat)`)|An entry in `coordinates` (`DataVariable`)|Distinguishes indexing values from primary data — see [Data Variable Concepts](#data-variable-concepts).|
|Spatial extent and CRS|`spatialCoverage`|Same `Place`/`GeoShape`/`SpatialReference` pattern as vector/raster data.|
|Source file or Zarr store|`associatedMedia`|A single `MediaObject`; `contentUrl` is a `gs://` or `s3://` URL for cloud-hosted Zarr stores.|

Resulting JSON-LD for a Zarr store on cloud object storage (`gs://cesm2/ivt.zarr`),
abbreviated to one variable:

``` json
{
    "@context": "https://hydroshare.org/schema",
    "@type": "ScientificDataset",
    "additionalType": "MultiDimensional",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": "-90.0 0.0 90.0 358.75"
        }
    },
    "associatedMedia": [
        {
            "@type": "MediaObject",
            "name": "ivt.zarr",
            "contentUrl": "gs://cesm2/ivt.zarr",
            "encodingFormat": "application/vnd+zarr",
            "contentSize": "40.5 GB"
        }
    ],
    "variableMeasured": [
        {
            "@type": "DataVariable",
            "name": "IVT",
            "dimensions": [
                "time",
                "lat",
                "lon"
            ],
            "description": "Total (vertically integrated) vapor transport",
            "dataType": "float16",
            "unit": "kg/m/s"
        }
    ],
    "dimensions": [
        {
            "@type": "Dimension",
            "name": "time",
            "shape": 366462,
            "description": "time"
        },
        {
            "@type": "Dimension",
            "name": "lat",
            "shape": 721
        },
        {
            "@type": "Dimension",
            "name": "lon",
            "shape": 574
        }
    ],
    "coordinates": [
        {
            "@type": "DataVariable",
            "name": "time",
            "dimensions": [
                "time"
            ]
        },
        {
            "@type": "DataVariable",
            "name": "lat",
            "dimensions": [
                "lat"
            ]
        },
        {
            "@type": "DataVariable",
            "name": "lon",
            "dimensions": [
                "lon"
            ]
        }
    ]
}
```

## Tabular Data

[`tabular.ipynb`](../notebooks/tabular.ipynb) demonstrates encoding **CSV** files
(including a tab-separated **USGS NWIS** file) and **Parquet** files. A table's row
index becomes a single dimension, the index itself becomes a coordinate variable, and
every column becomes a data variable over that dimension.

|File Structure|Maps To|Notes|
|---|---|---|
|The dataframe's row index (or a named datetime index)|`dimensions[0]` (`Dimension`) and `coordinates[0]` (`DataVariable`)|`Dimension.shape` is the row count; the matching `coordinates` entry captures the index's `dataType`, `minValue`, and `maxValue`.|
|Each column|An entry in `variableMeasured` (`DataVariable`)|`dimensions` is set to the index name; `minValue`/`maxValue` are computed only for numeric columns. When column metadata is available in a header (e.g., a custom USGS-style CSV), `unit`, `description`, and `noDataValue` are also populated.|
|Source file (CSV, tab-separated text, or Parquet, local or cloud-hosted)|`associatedMedia`|A single `MediaObject`; `contentUrl` may be an `s3://` URL for cloud-hosted Parquet.|

Resulting JSON-LD for a CSV file (`data/LR_GC_C_SourceID_1_QC_0_Year_2014.csv`),
abbreviated to two columns:

``` json
{
    "@context": "https://hydroshare.org/schema",
    "@type": "ScientificDataset",
    "additionalType": "Tabular",
    "associatedMedia": [
        {
            "@type": "MediaObject",
            "name": "LR_GC_C_SourceID_1_QC_0_Year_2014.csv",
            "contentUrl": "https://hydroshare.org/my-resource/data/LR_GC_C_SourceID_1_QC_0_Year_2014.csv",
            "encodingFormat": "text/csv",
            "contentSize": "16169.54 KB"
        }
    ],
    "variableMeasured": [
        {
            "@type": "DataVariable",
            "name": "LocalDateTime",
            "dimensions": [
                "index"
            ],
            "dataType": "object"
        },
        {
            "@type": "DataVariable",
            "name": "AirTemp_HC2S3_Max",
            "dimensions": [
                "index"
            ],
            "dataType": "float64",
            "minValue": "-9999.0",
            "maxValue": "25.36"
        }
    ],
    "dimensions": [
        {
            "@type": "Dimension",
            "name": "index",
            "shape": 35040
        }
    ],
    "coordinates": [
        {
            "@type": "DataVariable",
            "name": "index",
            "dimensions": "index",
            "dataType": "int64",
            "minValue": "0",
            "maxValue": "35039"
        }
    ]
}
```

When column metadata is parsed from a header (as with the USGS-style CSV in the
notebook), each `DataVariable` can additionally include `unit`, `description`, and
`noDataValue`:

``` json
{
    "@type": "DataVariable",
    "name": "AirTemp_HC2S3_Max",
    "dimensions": "DateTimeUTC",
    "description": "Air temperature measured using a Campbell Scientific HC2S3 temperature and relative humidity sensor. Maximum over 15 minutes.",
    "dataType": "float64",
    "unit": "degree celsius",
    "minValue": "-9999.0",
    "maxValue": "25.36",
    "noDataValue": "-9999.0"
}
```

The Parquet example (read directly from
`s3://us-west-2.opendata.source.coop/giswqs/nwi/wetlands/MA_Wetlands.parquet`) follows
the exact same mapping — only `associatedMedia.contentUrl` and `encodingFormat` differ.

## Spatial Reference System

[`spatial-reference-system.ipynb`](../notebooks/spatial-reference-system.ipynb)
demonstrates how `SpatialReference` (used inside `spatialCoverage.srs` in the vector,
raster, and multi-dimensional examples above) represents a coordinate reference
system.

|CRS Type|`srsType`|Example|
|---|---|---|
|Geographic (coordinates in degrees)|`geographic`|WGS 1984 ([EPSG:4326](https://spatialreference.org/ref/epsg/4326/))|
|Projected (coordinates in linear units, e.g., meters)|`projected`|WGS 84 / EPSG Arctic Regional zone B2 ([EPSG:5927](https://spatialreference.org/ref/epsg/5927/wkt.html))|

``` json
{
    "@type": "SpatialReference",
    "name": "WGS 84",
    "srsType": "geographic",
    "code": "EPSG:4326"
}
```

``` json
{
    "@type": "SpatialReference",
    "name": "WGS 84 / EPSG Arctic Regional zone B2",
    "srsType": "projected",
    "code": "EPSG:5927"
}
```

## Data Variable Concepts

[`datavariable.ipynb`](../notebooks/datavariable.ipynb) summarizes the conceptual
distinction used throughout the examples above:

|Component|What it Describes|Example|Appears In|
|---|---|---|---|
|Dimension|Size/extent of an axis|`time = 12`, `lat = 90`|`dimensions`|
|Variable|Main data array(s)|`temp(time, lat, lon)`|`variableMeasured`|
|Coordinate Variable|Values that exist along a dimension, sharing its name|`lat(lat)`, `time(time)`|`coordinates`|

See [Data Variable and Dimension Metadata](datavariable.md) for the full property
reference for `Dimension` and `DataVariable`.
