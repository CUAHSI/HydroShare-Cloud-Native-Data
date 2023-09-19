#!/bin/bash

# Specify the output path
OUTPUT="$(pwd)/output"

# Create the output directory
if [ ! -d "$OUTPUT" ]; then
	mkdir -p "$OUTPUT"
else
	rm -f "$OUTPUT"/*
fi

# Define the docker image name 
IMAGE="igarousi/nwm-subset:v1.2.4"

# Run the docker container
docker run --rm -ti \
	-v /home/igarousi/domain-subsetter/argo/nwm-v1/nwm.v1.2.4:/srv/domain \
	-v $OUTPUT:/srv/output \
        $IMAGE 382582.18746 1720355.72762 367584.87840 1734488.45260 /srv/domain /srv/output

