#!/bin/bash

# specify the folder path
folder="$(pwd)/output"

# create the output directory
if [ ! -d "$folder" ]; then
	mkdir -p "$folder"
else
	rm -f "$folder"/*
fi

# define docker image and output directory
IMAGE="cuahsi/cfe-configure:latest"
OUTPUT="$(pwd)/output"

# run the docker
# The two input arguments are for the following example are wb-2915523 (outlet catchment) and 16 (VPU ID)
docker run --rm -ti \
	-v $(pwd)/entry.py:/srv/entry.py \
	-v $(pwd)/subset.py:/srv/configure.py \
	-v $(pwd)/input-data:/srv/input \
	-v $OUTPUT:/srv/output \
	--entrypoint=/bin/bash \
	$IMAGE


#wb-2915523 16 
        
