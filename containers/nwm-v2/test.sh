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
IMAGE="igarousi/nwm-subset-test:v2.0"

# Run the docker container
#docker run --rm -ti \
#	-v /home/igarousi/nwm-data/nwm.v2.1:/srv/domain \
#	-v $OUTPUT:/srv/output \
#        $IMAGE 382582.18746 1720355.72762 367584.87840 1734488.45260 /srv/domain /srv/output

# Interactive mode test. When activated:
# Make sure the above docker run command is commented.
# Also, the last line of the Docker image (ENTRYPOINT ...) should be commented.
docker run --rm -ti \
        -v /home/igarousi/nwm-data/nwm.v2.0.0:/srv/domain \
        -v $OUTPUT:/srv/output \
	--entrypoint=/bin/bash \
        $IMAGE 
