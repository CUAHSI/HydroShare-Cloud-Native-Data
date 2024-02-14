#!/bin/bash


python entry.py \
    output-data/wb-2917496_upstream_subset.gpkg \
    output-data/results.nc \
    output-data/cfe_noahowp_attributes.csv \
    output-data \
    --verbose
