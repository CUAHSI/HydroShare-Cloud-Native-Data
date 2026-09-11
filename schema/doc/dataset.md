# Scientific Dataset Metadata

To classify a record as a scientific dataset, `"@type": "ScientificDataset"` should be
used in the JSON schema. `ScientificDataset` is CUAHSI's extension of the Schema.Org
[`Dataset`](https://schema.org/Dataset) class (defined in `schema/src/dataset.py`) and
is used to describe file-level scientific content such as rasters, vectors,
multi-dimensional arrays, and tabular data. It extends [core metadata](core.md) with
additional scientific properties, and it also relaxes several `CoreMetadata` fields
(`name`, `description`, `url`, `identifier`, `creator`, `dateCreated`, `keywords`,
`license`, `provider`) from required to optional, since a `ScientificDataset` frequently
describes a single file that inherits much of that context from its parent resource.

The following table outlines the properties introduced or overridden by
`ScientificDataset`, encoded as `1` or `1+` for **required** and `0,1` or `0+` for
**optional** in the Cardinality column.

|Property|Class|Expected Type|Cardinality|Description|
|---|---|---|---|---|
|[variableMeasured](#variable-measured)|ScientificDataset|Text \| PropertyValue \| DataVariable|1+|The variables that are measured in or present within the dataset.|
|[dimensions](#dimensions)|ScientificDataset|Dimension|1+|The dimensions (axes) defined by the multi-dimensional/tabular/vector dataset.|
|[coordinates](#coordinates)|ScientificDataset|DataVariable|0+|Coordinate variables that provide values along a dimension.|
|[associatedMedia](#associated-media)|ScientificDataset|MediaObject|1+|The file(s) that encode this dataset. Unlike `CoreMetadata`, this field is **required** for a `ScientificDataset`.|
|[includedInDataCatalog](#included-in-datacatalog)|ScientificDataset|DataCatalog|0,1|A data catalog which contains this dataset.|
|[additionalProperty](#additional-property)|ScientificDataset|PropertyValue|0+|A property-value pair representing an additional characteristic of the dataset that doesn't fit into Schema.org.|
|[sourceOrganization](#source-organization)|ScientificDataset|Organization|0,1|The organization or person who created/provided the underlying data.|
|[additionalType](#additional-type)|ScientificDataset|AdditionalType|0,1|A controlled vocabulary term further classifying the dataset (e.g., `GeographicFeature`, `GeographicRaster`, `MultiDimensional`, `Tabular`).|
|[sharing_status](#sharing-status)|ScientificDataset|DefinedTerm|0,1|The HydroShare sharing status of the resource (`Public`, `Published`, `Private`, `Discoverable`).|

The following examples demonstrate how each of these properties may be implemented in
JSON+LD.

### Variable Measured

[`Schema:variableMeasured`](https://schema.org/variableMeasured) can be expressed as
`Text`, a [`Schema:PropertyValue`](https://schema.org/PropertyValue), or CUAHSI's
[`DataVariable`](datavariable.md) extension, the latter being preferred for scientific
data since it captures dimensions, data type, units, and min/max values. See
[Data Variable and Dimension Metadata](datavariable.md) for the full `DataVariable`
definition.

A simple example as text can be encoded as:

``` json
{
    "variableMeasured": "Water Temperature"
}
```

It is preferred for a measured variable to be expressed as a `DataVariable`, which ties
the variable back to a named dimension:

``` json
{
    "variableMeasured": [
        {
            "@type": "DataVariable",
            "name": "HUC_ID",
            "dimensions": "feature_index",
            "dataType": "int64",
            "minValue": 101900030406.0,
            "maxValue": 101900050705.0
        },
        {
            "@type": "DataVariable",
            "name": "geometry",
            "dimensions": "feature_index",
            "dataType": "geometry"
        }
    ]
}
```

### Dimensions

`dimensions` describes the axes of the dataset (e.g., rows, columns, bands, time,
feature index) via CUAHSI's [`Dimension`](datavariable.md) extension. Every
`ScientificDataset` must declare at least one dimension, and each `DataVariable` in
`variableMeasured` references a dimension by name.

``` json
{
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

### Coordinates

`coordinates` captures coordinate variables — `DataVariable` entries whose values run
along one of the declared `dimensions` (e.g., `lat(lat)`, `time(time)`). This is
distinct from `variableMeasured`, which represents the primary data variables (e.g.,
`temperature(time, lat, lon)`).

``` json
{
    "coordinates": [
        {
            "@type": "DataVariable",
            "name": "time",
            "dimensions": "time",
            "dataType": "datetime64[ns]"
        }
    ]
}
```

### Associated Media

Unlike `CoreMetadata`, where `associatedMedia` is optional, a `ScientificDataset` must
reference at least one `MediaObject` describing the file(s) that encode the dataset.

``` json
{
    "associatedMedia": [
        {
            "@type": "MediaObject",
            "contentUrl": "https://hydroshare.org/my-resource/data/watershed.shp",
            "encodingFormat": "application/x-esri-shapefile",
            "contentSize": "269.75390625 KB",
            "name": "watershed.shp",
            "sha256": "9baf1e4e4e5b1e4946714bf4c153a618791c4e0de006bfa84769fcb1cbaddfe8"
        }
    ]
}
```

### Included in DataCatalog

[`Schema:includedInDataCatalog`](https://schema.org/includedInDataCatalog) can be used
to show the data catalog containing a dataset. Unlike the generic Schema.org `Dataset`
class, `ScientificDataset.includedInDataCatalog` accepts a single `DataCatalog` rather
than a list, since a file-level dataset is typically catalogued in one place.

``` json
{
    "includedInDataCatalog": {
        "@type" :"DataCatalog",
        "name": "The USGS Science Data Catalog (SDC)",
        "description" : "The Science Data Catalog (SDC) is the official public and searchable index that aggregates descriptions of all public research data that have been published by the USGS.",
        "url":"https://data.usgs.gov/datacatalog/",
        "creator": {
            "@type": "Organization",
            "name": "U.S. Geological Survey",
            "url": "https://www.usgs.gov/"
        }
    }
}
```

### Additional Property

Same pattern as [core metadata's `additionalProperty`](core.md#additional-property):
a `propertyID`/`value` pair used to capture supplementary characteristics not covered
by Schema.org.

``` json
{
    "additionalProperty": [
        {
            "@type": "PropertyValue",
            "propertyID": "Feature Count",
            "value": 7
        },
        {
            "@type": "PropertyValue",
            "propertyID": "Field Count",
            "value": 10
        }
    ]
}
```

### Source Organization

[Schema:sourceOrganization](https://schema.org/sourceOrganization) refers to the
entity responsible for creating the underlying data. This entity may differ from the
`creator` of the parent resource defined in the [core metadata](core.md). For example,
a researcher could assemble a resource that incorporates data produced from various
data sources; the resource's `creator` is the researcher, but the `sourceOrganization`
of a given file may be the agency that originally produced it.

``` json
{
    "sourceOrganization": {
        "@type": "Organization",
        "name": "National Hydrography Dataset",
        "url": "https://www.usgs.gov/national-hydrography/national-hydrography-dataset"
    }
}
```

### Additional Type

`additionalType` for a `ScientificDataset` is restricted to the `AdditionalType`
controlled vocabulary defined in `schema/src/dataset.py`, used by applications to
provide format-specific behavior:

|Value|Description|
|---|---|
|`GeographicFeature`|Vector data (e.g., Shapefile, GeoJSON, GML).|
|`GeographicRaster`|Raster data (e.g., single/multi-band GeoTIFF, ASCII Raster).|
|`MultiDimensional`|Multi-dimensional array data (e.g., NetCDF, Zarr).|
|`Tabular`|Tabular data (e.g., CSV, Parquet, USGS NWIS tab-separated files).|

``` json
{
    "additionalType": "GeographicFeature"
}
```

### Sharing Status

`sharing_status` is a HydroShare-specific controlled vocabulary term (`Public`,
`Published`, `Private`, or `Discoverable`) describing the sharing status of the
resource that contains this dataset.

``` json
{
    "sharing_status": {
        "@type": "Public",
        "name": "Public",
        "description": "The resource is publicly accessible and can be viewed or downloaded by anyone"
    }
}
```

## Full Example

The example below shows a complete `ScientificDataset` record generated for a
Shapefile, combining `dimensions`, `variableMeasured` (as `DataVariable`),
`associatedMedia`, and `spatialCoverage` (see [core metadata](core.md#spatial-coverage)).
See [Example Implementations](examples.md) for equivalent worked examples for raster,
multi-dimensional, and tabular data, each referencing its source notebook in
`schema/notebooks/`.

``` json
{
    "@context": "https://hydroshare.org/schema",
    "@type": "ScientificDataset",
    "additionalType": "GeographicFeature",
    "spatialCoverage": {
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": "39.84727077900004 -105.700627563 40.15893526200006 -104.933629104"
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
            "contentUrl": "https://hydroshare.org/my-resource/data/watershed.shp",
            "encodingFormat": "application/x-esri-shapefile",
            "contentSize": "269.75390625 KB",
            "name": "watershed.shp",
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

## Editable Scientific Dataset

`EditableScientificDataset` (also defined in `schema/src/dataset.py`) is a restricted
subset of `ScientificDataset` used when a user edits a dataset's metadata through an
application form rather than regenerating it from the source file. It only exposes
the fields that a user is expected to hand-edit — `name`, `description`, `keywords`,
`license`, `provider`, `additionalProperty`, `funding`, `temporalCoverage`,
`spatialCoverage`, and `citation` — omitting fields that are derived directly from the
underlying data file (e.g., `variableMeasured`, `dimensions`, `coordinates`,
`associatedMedia`). The corresponding JSON Schema is generated to
`schema/src/json_schemas/editable_scientific_dataset_json_schema.json`, while the full
`ScientificDataset` JSON Schema is generated to
`schema/src/json_schemas/scientific_dataset_json_schema.json`.
