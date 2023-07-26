#!/bin/bash


docker run --rm \
    -v $(pwd)/output:/srv/output \
    -v $(pwd)/../../../notebooks/sample-data:/srv/shp-data \
    cuahsi/aorc:1.1 \
    "2010-01-01 00:00:00" \
    "2010-01-01 01:00:00" \
    /srv/shp-data/watershed.shp \
    /srv/output \
    --verbose
