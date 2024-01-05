#!/bin/bash


docker run --rm \
    -v $(pwd)/output:/srv/output \
    -v $(pwd)/../../../notebooks/sample-data:/srv/shp-data \
    cuahsi/aorc:latest \
    "2010-01-01 00:00:00" \
    "2010-01-01 09:00:00" \
    /srv/shp-data/watershed.shp \
    /srv/output \
    --timesteps-per-group=3 \
    --num-workers=3 \
    --worker-mem-limit=3GB \
    --verbose
