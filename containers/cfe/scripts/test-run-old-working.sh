#!/bin/bash

docker run --rm -ti \
    -v $(pwd)/working-example:/ngen/ngen/data \
    -v $(pwd)/run.sh:/ngen/run.sh \
    --entrypoint=/bin/bash \
    awiciroh/ciroh-ngen-image:latest-x86

# /dmod/bin/ngen-serial <catchment_data_path> all <nexus_data_path> all <realization_config_path>

#/dmod/bin/ngen-serial /ngen/ngen/data/catchments.geojson all /ngen/ngen/data/nexus.geojson all /ngen/ngen/data/config/realization.json
