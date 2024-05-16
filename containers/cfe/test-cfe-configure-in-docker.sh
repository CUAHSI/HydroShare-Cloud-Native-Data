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
INPUTS="$(pwd)/input-data"

# run the docker
# The two input arguments are for the following example: wb-2915523 (outlet catchment) and 16 (VPU ID)
docker run --rm -ti \
	-v $OUTPUT:/srv/output \
	-v $INPUTS:/srv/input \
	$IMAGE 
