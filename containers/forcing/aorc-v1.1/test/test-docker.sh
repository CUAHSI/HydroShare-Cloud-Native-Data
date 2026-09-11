#!/bin/bash

docker run --rm \
	-v $(pwd)/test-data:/app/test-data \
	cuahsi/aorc-v1.1:20240515 \
	2018-08-01 \
	2018-08-31 \
	/app/test-data/watershed.shp \
	s3://noaa-nwm-retrospective-3-0-pds \
	--n-workers=4 \
	--worker-memory=4
