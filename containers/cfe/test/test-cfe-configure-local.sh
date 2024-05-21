#!/bin/bash

root_path="test-data/small"
python ../entry.py \
	$root_path/domain/wb-2853612_upstream_subset.gpkg \
	$root_path/forcing/forcing.nc \
	$root_path/domain/cfe_noahowp_attributes.csv \
	$root_path/config \
	--verbose
