#!/bin/bash

python entry.py \
	test-data/small/domain/wb-2917533_upstream_subset.gpkg \
	test-data/small/forcing/results.nc \
	test-data/small/domain/cfe_noahowp_attributes.csv \
	test-data/small-out \
	--verbose
