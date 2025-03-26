# Dataset Metadata

To classify a record as a dataset, `"@type": "Dataset"` should be used in the json schema. This will classify the record as a specific Schema.Org type called `Dataset` for which the metadata should be described using the [core metadata](core.md), as well as the dataset-specific properties for the [Schema:Dataset](https://schema.org/Dataset) class. The following table outlines the required and optional properties selected from Schema.Org vocabulary, these properties are encoded as `1` or `1+` 
for **required** and `0,1` or `0+` for **optional** in the Cardinality column of the table below.

|Property|Class|Expected Type|Cardinality|Description|
|---|---|---|---|---|
|[additionalProperty](#additional-property)|Thing|PropertyValue|1+|A property-value pair representing an additional characteristic of the entity.|
|[variableMeasured](#variable-measured)| Dataset | Text \| PropertyValue | 0+ | The variableMeasured property can indicate (repeated as necessary) the variables that are measured in some dataset, either described as text or as pairs of identifier and description using PropertyValue. |
|[sourceOrganization](#source-organization)|Thing|Organization \| Person|0+|The organization or person who creates the data.|
|[includedInDataCatalog](#included-in-datacatalog)| Dataset | DataCatalog | 1+ | A data catalog which contains this dataset. |

The following examples demonstrate how each of these properties may
be implemented in JSON+LD. 

### Additional Property
[Schema:additionalProperty](https://schema.org/additionalProperty) represents a property-value pairing using, `propertyID` and `value` properties from Schema.org,  designed to accommodate supplementary information for an entity when no direct match exists within Schema.org. Both `propertyID` and `value` property remain user-defined and serves as the input provided by users.

A simple example of two user defined additional metadata is shown below:

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


### Variable Measured

[`Schema:variableMeasured`](https://schema.org/variableMeasured) is a property of the `Dataset` class and can be expressed as either `Text` or a [`Schema:PropertyValue`](https://schema.org/PropertyValue), the latter being preferred. The `variableMeasured` represents the scientific variables that are measured or present within the dataset. Note, the `PropertyValue` type contains a number of useful properties that may be implements including units, min/max values, etc. For a complete list of properties see the [`Schema:PropertyValue`](https://schema.org/PropertyValue) definition.

A simple example as text can be encoded as:

``` json
{
    "variableMeasured": "Water Temperature"
}
```
However, it is preferred for a measured variable to be expressed as a `PropertyValue`.

``` json
{     
    "variableMeasured": {
        "@type": "PropertyValue",
        "name": "Streambed interface temperature values",
        "unitText": "degC"
    }
}
```
Another example where multiple variables are measured:

``` json
{
    "variableMeasured": [
        {
            "@type": "PropertyValue",
            "propertyID": "air temperature",
            "value": "float64",
            "unitCode": "F",
            "description":"Basin's averaged air temperature"                      
        },
        {
            "@type": "PropertyValue",
            "propertyID": "areasqkm",
            "value": "float64",
            "unitCode": "square kilometers",
            "description":"Basin's area"                      
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


### Included in DataCatalog

DataCatalog comprises a set of datasets. [`Schema:includedInDataCatalog`](https://schema.org/includedInDataCatalog) can be used to show the data catalog containing a dataset. Essentially, every scientific dataset must have a minimum of one `DataCatalog` object. In some cases, certain records may feature more than one `DataCatalog` object represented in the `includedIndDataCatalog` property if they are part of other data catalogs. This property can be used as a filter to specify which data catalog(s) include a particular dataset. 

In the example below, we used the `includedInDataCatalog` property to show that the dataset is included in the U.S. Geological Survey Science Data Catalog (SDC).

``` json
{
    "includedInDataCatalog": [
        {
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
    ] 
}
```
