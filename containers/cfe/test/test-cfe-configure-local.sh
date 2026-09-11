#!/bin/bash

root_path="test-data/small"
out_path="test-data/small-out"
python ../src/entry.py \
	$root_path/domain/wb-2853612_upstream_subset.gpkg \
	$root_path/forcing/forcing.nc \
	$root_path/domain/cfe_noahowp_attributes.csv \
	$out_path \
	--verbose
