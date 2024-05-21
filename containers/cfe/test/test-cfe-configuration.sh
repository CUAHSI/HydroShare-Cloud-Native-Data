#!/bin/bash

test_data_root=./test-data/small

echo 'Running Test on Dir: ' $test_data_root

gpkg_name=$(find $test_data_root -name "*.gpkg")
python ../entry.py \
	$gpkg_name \
	$test_data_root/forcing/forcing.nc \
	$test_data_root/domain/cfe_noahowp_attributes.csv \
	small-out \
	1 \
	10 \
	--verbose

echo 'Test Complete'
