#!/bin/bash

python ../entry.py \
	2018-08-01 \
	2018-08-31 \
	test-data/watershed.shp \
	s3://noaa-nwm-retrospective-3-0-pds \
	--n-workers=4 \
	--worker-memory=4
