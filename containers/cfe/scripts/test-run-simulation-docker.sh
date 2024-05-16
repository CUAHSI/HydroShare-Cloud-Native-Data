#!/bin/bash

## Test newly generated configs
# config_data_path=$(realpath "../notebooks/config")
# catchments_geojson_path=$(realpath "../test-data/domain/catchments.geojson")
# nexus_geojson_path=$(realpath "../test-data/domain/nexus.geojson")

## Test old, "working" configs

# catchments_geojson_path=$(realpath "../notebooks/my-simulation/domain/catchments.geojson")
# nexus_geojson_path=$(realpath "../notebooks/my-simulation/domain/nexus.geojson")

#root_data_path=$(realpath /tmp/ngen/data/gauge_01073000)
root_data_path=$(realpath "../notebooks/data")
#root_data_path=$(realpath "../extra/old-stuff/working-example")
echo $root_data_path
docker run --rm -ti \
	--mount type=bind,source=$root_data_path,target=/ngen/data \
	--mount type=bind,source=$(pwd)/run.sh,target=/ngen/run.sh \
	--entrypoint=/bin/bash \
	cuahsi/ngiab:v0.1

#-c "bash run.sh"
