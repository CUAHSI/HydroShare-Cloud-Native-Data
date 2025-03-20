# Geopackage

A [GeoPackage](https://www.geopackage.org/) is an open, standards-based format for storing and transfering geospatial information. A GeoPackage is an aggregation of various data types, including vectors, rasters, and tabular data (typically non-geometric). Therefore, it can be represented using the `hasPart` property from the Schema.org vocabulary, which is used to define relationships between components. At the core level of the schema, the `hasPart` property refers to one or more JSON files containing metadata about the content. This includes a metadata JSON file describing the entire resource, as well as additional metadata JSON files for individual files (see below).

### *HasPart from the core metadata represented at the **core level***
The `HasPart` property, as described in the core metadata, can encompass a collection of things that represent the work. In the case of a geopackage file type, the configuration of the `HasPart` property is outlined below. 

``` json
{
  "hasPart": [
    {
        "@type": "CreativeWork",
        "name": "nextgen_18.gpkg.json",
        "description": "The metadata json file for the shapefile.",
        "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json"
    }
  ]
}
```

Since GeoPackage is a file that contains different things (creativeworks), withing its associated JSON metadata file, the `hasPart` property is used again at a second level within the **nextgen_18.gpkg.json** file to describe the individual components of the GeoPackage. These components—vector layers, raster datasets, and tabular data—are each represented as separate entities under this nested hasPart structure. Note that the first item in `hasPast` always refers to the metadata file itself that is describing the work.

### *HasPart from the core metadata represented at the **file level***
The `hasPart` property at this second level includes 

``` json
{
  "hasPart": [
    {
        "@type": "Dataset",
        "name": "vector_layer_name",
        "description": "The vector layer of the geopackage.",
        "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?vector=table_layer_name"
    },
    {
        "@type": "Dataset",
        "name": "raster_layer_name",
        "description": "The raster layer of the geopackage.",
        "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?table=raster_layer_name"
    },
    {
        "@type": "Dataset",
        "name": "table_layer_name",
        "description": "The table layer of the geopackage.",
        "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?table=table_layer_name"
    }
  ]
}
```

The following **required** and **optional** properties, based on Schema.Org vocabulary, are suggested for describing the component of a GeoPackage. Both `additionalProperty` and `variableMeasured` are represented using the `PropertyValue` class but with a key distinction. In `additionalProperty`, the terms assigned to `propertyID` are **predefined and fixed**, ensuring consistency in metadata representation. In contrast, `variableMeasured` allows `propertyID` values to be **dynamically extracted** from the content, providing flexibility based on the available data. These properties will enhance the [core metadata](core.md) represented in each of the Geopackage's component JSON files.

|Property|Class|Expected Type|Cardinality|Description|
|---|---|---|---|---|
|[additionalProperty](#additional-property)|Thing|PropertyValue|1+|A property-value pair representing an additional characteristic of the entity.|
|[variableMeasured](#variable-measured)|Thing|Number \| Text|1+|A variable that is measured or estimated.|
|[sourceOrganization](#source-organization)|Thing|Organization \| Person|0+|The organization or person who creates the data.|

### Additional Property

[Schema:additionalProperty](https://schema.org/additionalProperty) represents a property-value pairing designed to accommodate supplementary information for an entity when no direct match exists within Schema.org. In this context, the `propertyID` consists of **predefined fixed** terms. When using **fixed terms**, `propertyID` ensures consistency, while the `value` property remains user-defined and serves as the input provided by users. Given that a GeoPackage can store multiple vector layers (like shapefiles) and raster layers (like GeoTIFFs) in a single container, we intend to use the `additionalProperty` class to describe key metadata elements of its contents:

#### Vectors
For a **vector** component, we intend to use the `additionalProperty` property to denote both the count of features and fields within a shapefile. "Features" within a shapefile denote individual geographic objects, such as point, line, or polygon, and encompass both spatial geometry and associated attribute data. In the context of shapefile, the term "fields" refer to the columns present in the attribute table. The attribute table is a tabular structure where each row corresponds to a feature in the shapefile, and each column (or field) represents a different attribute or type of information associated with those features. To embody the feature and field counts, we use the `propertyID` and `value` attributes within the `additionalProperty` class. 

|PropertyID|PropertyID Category|Expected Value Type|Cardinality|Description|
|---|---|---|---|---|
|Feature Count|Fixed|int|1|Individual geographic objects (such as point, line, or polygon) that encompass both spatial geometry and associated attribute data.|
|Field Count|Fixed|int|1|Columns present in the attribute table of the shapefile.|

A simple example of a GeoPackage's shapefile layer with 7 features (polygons) and 10 fields (attributes) is shown below:

``` json
{
    "additionalProperty": [
        {
            "@type": "PropertyValue",
            "PropertyID": "Feature Count",
            "value": 7
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Field Count",
            "value": 10
        }
    ]
}
```

#### Rasters
For a **raster** component, we intend to use the `additionalProperty` property to denote the *Cell Information* including the number of rows and columns, the spatial resolution of a grid cell, and the data type associated with the grid cells. Note that the `propertyID` for rasters consists of fixed terms that we have assigned to these pairs, ensuring consistency, while the value property remains user-defined and serves as the input provided by users.

|PropertyID|PropertyID Category|Expected Value Type|Cardinality|Description|
|---|---|---|---|---|
|Rows |Fixed|int|1|The number of rows (height) in the raster grid.|
|Columns |Fixed|int|1|The number of columns (width) in the raster grid.|
|Cell Size X Value|Fixed|Float32|1,0|The spatial resolution of a grid cell along the east-west (X) direction, representing the width of each cell in meters or degrees.|
|Cell Size Y Value|Fixed|Float32|1,0|The spatial resolution of a grid cell along the north-south (Y) direction, representing the height of each cell in meters or degrees.|
|Cell Data Type|Fixed|string|1,0|The data type of the raster cell values (e.g., Float32, Int16, Byte), defining how pixel values are stored.|

A simple example of a GeoPackage's geotiff layer with one band is shown below:

``` json
{
    "additionalProperty": [
        {
            "@type": "PropertyValue",
            "PropertyID": "Rows",
            "value": 4981
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Columns",
            "value": 2956
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Cell Size X Value",
            "value": 10.0
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Cell Size Y Value",
            "value": 10.0
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Cell Data Type",
            "value": "Float32"
        }
    ]
}
```

#### Tables
For a **table** component, we intend to use the `additionalProperty` property to represent both the row and column count within non-geometry data in a GeoPackage. Note that the `propertyID` for representing the `additonalProperty` of tables consists of fixed terms. These tables does not include spatial information but is still valuable for geospatial analysis. Common types of non-geometry tables in a GeoPackage include:
* Attribute Tables – Store attributes related to spatial layers but do not contain geometries themselves.
* Lookup Tables – Contain classification schemes or reference data.
* Time-Series Data – Store data linked to locations but without direct spatial geometry.
* Raster Metadata Tables – Describe raster layers stored within the GeoPackage.
* Statistical Summary Tables – Typically derived from raster data, providing aggregated statistics for measured variables.

|PropertyID|PropertyID Category|Expected Value Type|Cardinality|Description|
|---|---|---|
|Row Count |Fixed|int|1|The number of rows in the table.|
|Column Count |Fixed|int|1|The number of columns in the table.|

A simple example of a GeoPackage's tabular layer with two rows and one column is shown below:

``` json
{
    "additionalProperty": [
        {
            "@type": "PropertyValue",
            "PropertyID": "Row Count",
            "value": 3
        },
        {
            "@type": "PropertyValue",
            "PropertyID": "Column Count",
            "value": 2
        }
    ]
}
```

### Variable Measured

[Schema:variableMeasured](https://schema.org/variableMeasured) is a property of the `Thing` class. This property can be employed via the `PropertyValue` class, incorporating a set of required and optional properties (as shown in the table below) to describe the metadata corresponding to the attributes within a component of a GeoPackage. In this context, the `propertyID` consists of  **dynamically extracted** terms. When using **dynamic** terms, `propertyID` values are automatically extracted from the file, allowing flexibility in representing varying attributes.

|Property|Property Category|Expected Value Type|Cardinality|Description|
|---|---|---|---|---|
|PropertyID |Dynamic|string|1|The name of a variable measured. |
|value| Dynamic|string \| integer \| float \| real|1|Specifies the data type of the variable or variable measured. |
|unitCode| Dynamic|string|0,1|The unit of a variable measured.|
|minValue |Dynamic| string|1,0|The minimum value of a variable measured.|
|maxValue |Dynamic| string|1,0|The maximum value of a variable measured.|
|description |Dynamic| string|1,0|A description of a variable measured.|

#### Vectors

A simple example of a GeoPackage's shapefile layer with 10 fields (variables) is shown below:

``` json
{
    "variableMeasured": [
        {
            "@type": "PropertyValue",
            "propertyID": "objectid",
            "value": "float64"                   
        },
        {
            "@type": "PropertyValue",
            "propertyID": "areaacres",
            "value": "float64",
            "unitCode": "acres",
            "description":"The polygon's area"                      
        },
        {
            "@type": "PropertyValue",
            "propertyID": "areasqkm",
            "value": "float64",
            "unitCode": "square kilometers",
            "description":"The polygon's area"                      
        },
        {
            "@type": "PropertyValue",
            "propertyID": "states",
            "value": "object"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "huc12",
            "value": "object",
            "description": "Unique hydrologic unit code"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "name",
            "value": "object",
            "description":"GNIS name for the geographic area in which the hydrologic unit is located"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "tohuc",
            "value": "object",
            "description": "Code for the 12-digit hydrologic unit that is downstream from and naturally receives the majority of the flow from this unit"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "shape_Leng",
            "value": "float64"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "shape_Area",
            "value": "float64"                    
        },
        {
            "@type": "PropertyValue",
            "propertyID": "geometry",
            "value": "geometry"   
        }
    ]
}
```

#### Rasters

A simple example of a GeoPackage's geotiff layer with one band that represents the elevation of each grid cell is shown below:

``` json
{
    "variableMeasured": [
        {
            "@type": "PropertyValue",
            "propertyID": "Elevation",
            "value": "float32",
            "unitCode": "m",
            "minValue": "1358.2",
            "maxValue": "3040.8",
            "description": "Digital Elevation Model",                   
        }
    ]
}
```

#### Tables

A simple example of a GeoPackage's tabular layer with three rows (variables) and two column is shown below:

``` json
{
    "variableMeasured": [
        {
            "@type": "PropertyValue",
            "propertyID": "fid",
            "value": "Integer64",
            "description": "The unique identifier of the rivers.",
        },
        {
            "@type": "PropertyValue",
            "propertyID": "lengthkm",
            "value": "Real",
            "unitCode": "m",
            "minValue": "0.1",
            "maxValue": "1500.0", 
            "description": "The slope of a river.", 
        },
        {
            "@type": "PropertyValue",
            "propertyID": "ChSlp",
            "value": "Real",
            "unitCode": "-",
            "description": "The slope of a river.", 
        }
    ]
}
```

### Source Organization
[Schema:sourceOrganization](https://schema.org/sourceOrganization) refers to the entity responsible for creating the shapefile. This entity may differ from the creator of the resource, as defined in the [core metadata](core.md). For example, a researcher could assemble a resource that incorporates data produced from various data sources. In this scenario, the creator of the resource in the researcher; however, the organization or individual that originally formulated the dataset might diverge from the researcher's identity.

``` json
{
    "sourceOrganization": {
        "@type": "Organization",
        "name": "National Hydrography Dataset",
        "url": "https://www.usgs.gov/national-hydrography/national-hydrography-dataset"
    }
}
```





### Supplemental Properties from the Core Metadata
Please note that any property from our [core metadata](core.md) can potentially be added into the schema for each of the layers. In the context of vectors and rasters `spatialCoverage`, we are using the `additionalProperty` attribute to define both geographical and projected coordinate systems. This dual representation is helpful to enhance accuracy, interoperability, versatility, and contextual flexibility. 

|PropertyID|Property Category|Expected Value Type|Cardinality|Description|
|---|---|---|---|---|
|Geographic Coordinate System|Fixed|String|1|The geographic coordinate system (GCS) used to define locations on Earth, typically referenced with an EPSG code (e.g., `WGS 84 EPSG:4326`).|
|Coordinate Reference System|Fixed|String|1,0|The complete coordinate reference system (CRS) defining how coordinates are projected onto a plane, such as `North_America_Albers_Equal_Area_Conic`.|
|Datum|Fixed|String|1,0|The geodetic datum that provides a frame of reference for coordinate measurements, such as `North_American_Datum_1983`.|
|Unit|Fixed|String|1,0|The measurement unit used for coordinates in the CRS, typically `Meter` for projected coordinate systems.|
|Coordinate String|Fixed|String|1,0|The full coordinate reference system (CRS) definition in PROJ.4 or WKT (Well-Known Text) format, describing all projection parameters in detail.| 


```json
{
"spatialCoverage": {
    "@type": "Place",
    "name": "Logan Watershed",
    "geo": {
        "@type": "GeoShape",
        "box": "41.70049003694901 -111.78438452093438 42.102360645589236 -111.51208495002092"
    },
    "additionalProperty": [
        {
            "@type": "PropertyValue",
            "propertyID": "Coordinate System",
            "value": "WGS 84 EPSG:4326" 
        },
        {
            "@type": "PropertyValue",
            "propertyID": "Coordinate Reference System",
            "value": "North_America_Albers_Equal_Area_Conic" 
        }, 
        {
            "@type": "PropertyValue",
            "propertyID": "Datum",
            "value": "North_American_Datum_1983" 
        }, 
        {
            "@type": "PropertyValue",
            "propertyID": "Unit",
            "value": "Meter" 
        },
        {
            "@type": "PropertyValue",
            "propertyID": "Coordinate String",
            "value": "PROJCS['North_America_Albers_Equal_Area_Conic', GEOGCS['GCS_North_American_1983', DATUM['North_American_Datum_1983', SPHEROID['GRS_1980',6378137.0,298.257222101]], PRIMEM['Greenwich',0.0], UNIT['Degree',0.0174532925199433]], PROJECTION['Albers_Conic_Equal_Area'], PARAMETER['False_Easting',0.0], PARAMETER['False_Northing',0.0], PARAMETER['longitude_of_center',-96.0], PARAMETER['Standard_Parallel_1',20.0], PARAMETER['Standard_Parallel_2',60.0], PARAMETER['latitude_of_center',40.0], UNIT['Meter',1.0], AUTHORITY['Esri','102008']]" 
        }
    ]
}
}
```


### A Complete Example for a GeoPackage

Here is a complete example of a GeoPackage that integrates all the information discussed above. **One key distinction is the absence of `associatedMedia` for GeoPackage layers represented by the `hasPart` class, which would typically be present if each layer were a separately downloadable file.** Comparing the properties under hasPart in the following example with those in the complete examples for Shapefile or GeoTIFF files highlights this difference.

``` json
{
    "@type": "Dataset",
    "name": "nextgen_18.gpkg",
    "description": "The hydrofabric data for hydrological zone 18, prepared to be used in the NextGen hydrological modeling framework.",
    "url": "https://www.hydroshare.org/resource/fed970c19b9c41928f2591adf5b64dd1/data/contents/nextgen_18.gpkg",
    "associatedMedia": {
        "@type": "DataDownload",
        "contentUrl": "https://www.hydroshare.org/resource/fed970c19b9c41928f2591adf5b64dd1/data/contents/nextgen_18.gpkg",
        "encodingFormat": "application/geopackage+sqlite3",
        "sha256": "",
        "contentSize": "176.2 MB"
    },
    "hasPart": [
        {
            "@type": "Dataset",
            "name": "vector_layer_name",
            "description": "The vector layer of the geopackage.",
            "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?vector=table_layer_name",
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Feature Count",
                    "value": 7
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Field Count",
                    "value": 10
                }
            ],
            "variableMeasured": [
                {
                    "@type": "PropertyValue",
                    "propertyID": "objectid",
                    "value": "float64"                   
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "areaacres",
                    "value": "float64",
                    "unitCode": "acres",
                    "description":"The polygon's area"                      
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "areasqkm",
                    "value": "float64",
                    "unitCode": "square kilometers",
                    "description":"The polygon's area"                      
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "states",
                    "value": "object"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "huc12",
                    "value": "object",
                    "description": "Unique hydrologic unit code"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "name",
                    "value": "object",
                    "description":"GNIS name for the geographic area in which the hydrologic unit is located"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "tohuc",
                    "value": "object",
                    "description": "Code for the 12-digit hydrologic unit that is downstream from and naturally receives the majority of the flow from this unit"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "shape_Leng",
                    "value": "float64"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "shape_Area",
                    "value": "float64"                    
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "geometry",
                    "value": "geometry"   
                }
            ],
            "spatialCoverage": {
                "@type": "Place",
                "name": "Logan Watershed",
                "geo": {
                    "@type": "GeoShape",
                    "box": "41.70049003694901 -111.78438452093438 42.102360645589236 -111.51208495002092"
                },
                "additionalProperty": [
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate System",
                        "value": "WGS 84 EPSG:4326" 
                    },
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate Reference System",
                        "value": "North_America_Albers_Equal_Area_Conic" 
                    }, 
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Datum",
                        "value": "North_American_Datum_1983" 
                    }, 
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Unit",
                        "value": "Meter" 
                    },
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate String",
                        "value": "PROJCS['North_America_Albers_Equal_Area_Conic', GEOGCS['GCS_North_American_1983', DATUM['North_American_Datum_1983', SPHEROID['GRS_1980',6378137.0,298.257222101]], PRIMEM['Greenwich',0.0], UNIT['Degree',0.0174532925199433]], PROJECTION['Albers_Conic_Equal_Area'], PARAMETER['False_Easting',0.0], PARAMETER['False_Northing',0.0], PARAMETER['longitude_of_center',-96.0], PARAMETER['Standard_Parallel_1',20.0], PARAMETER['Standard_Parallel_2',60.0], PARAMETER['latitude_of_center',40.0], UNIT['Meter',1.0], AUTHORITY['Esri','102008']]" 
                    }
                ]
            },
            "temporalCoverage": {
                "@type": "DateTime",
                "startDate": "",
                "endDate": ""
            },
            "sourceOrganization": {
                "@type": "Organization",
                "name": "National Hydrography Dataset",
                "url": "https://www.usgs.gov/national-hydrography/national-hydrography-dataset"
            }
        },
        {
            "@type": "Dataset",
            "name": "raster_layer_name",
            "description": "The raster layer of the geopackage.",
            "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?table=raster_layer_name",
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Rows",
                    "value": 4981
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Columns",
                    "value": 2956
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Cell Size X Value",
                    "value": 10.0
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Cell Size Y Value",
                    "value": 10.0
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Cell Data Type",
                    "value": "Float32"
                }
            ],
            "variableMeasured": [
                {
                    "@type": "PropertyValue",
                    "propertyID": "Elevation",
                    "value": "float32",
                    "unitCode": "m",
                    "minValue": "1358.2",
                    "maxValue": "3040.8",
                    "description": "Digital Elevation Model",                   
                }
            ],
            "spatialCoverage": {
                "@type": "Place",
                "name": "Logan Watershed",
                "geo": {
                    "@type": "GeoShape",
                    "box": "41.70049003694901 -111.78438452093438 42.102360645589236 -111.51208495002092"
                },
                "additionalProperty": [
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate System",
                        "value": "WGS 84 EPSG:4326" 
                    },
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate Reference System",
                        "value": "North_America_Albers_Equal_Area_Conic" 
                    }, 
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Datum",
                        "value": "North_American_Datum_1983" 
                    }, 
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Unit",
                        "value": "Meter" 
                    },
                    {
                        "@type": "PropertyValue",
                        "propertyID": "Coordinate String",
                        "value": "PROJCS['North_America_Albers_Equal_Area_Conic', GEOGCS['GCS_North_American_1983', DATUM['North_American_Datum_1983', SPHEROID['GRS_1980',6378137.0,298.257222101]], PRIMEM['Greenwich',0.0], UNIT['Degree',0.0174532925199433]], PROJECTION['Albers_Conic_Equal_Area'], PARAMETER['False_Easting',0.0], PARAMETER['False_Northing',0.0], PARAMETER['longitude_of_center',-96.0], PARAMETER['Standard_Parallel_1',20.0], PARAMETER['Standard_Parallel_2',60.0], PARAMETER['latitude_of_center',40.0], UNIT['Meter',1.0], AUTHORITY['Esri','102008']]" 
                    }
                ]
            },
            "sourceOrganization": {
                "@type": "Organization",
                "name": "National Hydrography Dataset",
                "url": "https://www.usgs.gov/national-hydrography/national-hydrography-dataset"
            }
        },
        {
            "@type": "Dataset",
            "name": "table_layer_name",
            "description": "The table layer of the geopackage.",
            "url": "https://www.hydroshare.org/.../nextgen_18.gpkg.json/?table=table_layer_name",
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Row Count",
                    "value": 3
                },
                {
                    "@type": "PropertyValue",
                    "PropertyID": "Column Count",
                    "value": 2
                }
            ],
            "variableMeasured": [
                {
                    "@type": "PropertyValue",
                    "propertyID": "fid",
                    "value": "Integer64",
                    "description": "The unique identifier of the rivers.",
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "lengthkm",
                    "value": "Real",
                    "unitCode": "m",
                    "minValue": "0.1",
                    "maxValue": "1500.0", 
                    "description": "The slope of a river.", 
                },
                {
                    "@type": "PropertyValue",
                    "propertyID": "ChSlp",
                    "value": "Real",
                    "unitCode": "-",
                    "description": "The slope of a river.", 
                }
            ]
        }
  ]
}
```

