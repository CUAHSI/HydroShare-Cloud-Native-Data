# NGEN Domain Subsetting

**Description**: This workflow extracts the NGEN HydroFabric for a region
upstream of a provided watershed boundary identifier. The resulting subset
domain consists of a series of data files that can be used to run a model
simulation within the NGEN Modeling Framework.

## Workflow Input

- `wb-id`: waterbody identifier from the NGEN HydroFabric
- `vpu-id` vector processing unit identifier from the NGEN HydroFabric
- `hydrofabric-url`: url to the HydroFabric data on S3
- `output-bucket`: name of cloud bucket to save output data
- `output-path`: path within `output-bucket` to save job outputs


## Workflow Output

**Subsetted Domain** 
- description: subsetted NGEN domain files upstream of the provided `wb-id`. 
- location: `{output-bucket}/{output-path}/domain`

## Example 


**CLI Command**
```
argo submit ngen-subset-v2.0.yaml \
  -p wb-id="wb-2917533" \
  -p vpu-id="16" \
  -p hydrofabric-url="s3://lynker-spatial/v20/gpkg/" \
  -p output-path="my-subsetting-job" \
  -p output-bucket="subsetter-outputs"
```

**Results**

```
catchments.geojson
cfe_noahowp_attributes.csv
crosswalk.json
flowpath_edge_list.json
flowpaths.geojson
nexus.geojson
watershed.gz
wb-2917533_upstream_subset.gpkg
```
