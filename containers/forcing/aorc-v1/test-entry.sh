#!/bin/bash

python entry.py \
    "2010-01-01 00:00:00" \
    "2010-01-01 09:00:00" \
    $(pwd)/../../../notebooks/sample-data/watershed.shp \
    $(pwd)/output \
    --timesteps-per-group=3 \
    --verbose

