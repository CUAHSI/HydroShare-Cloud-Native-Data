#!/bin/bash


python entry.py \
    input-data/wb-2917533_upstream_subset.gpkg \
    input-data/results.nc \
    input-data/cfe_noahowp_attributes.csv \
    output-data \
    --verbose
