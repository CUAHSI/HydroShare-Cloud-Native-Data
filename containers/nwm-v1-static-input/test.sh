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
#IMAGE="cuahsi/nwm-subset:v2.1"
IMAGE='us-central1-docker.pkg.dev/apps-320517/subsetter/nwm:1.8'

#DOMAIN='/Volumes/ColdStorage/nwm.v1.2.4'
#DOMAIN='/Volumes/ColdStorage/subsetter/domain-data/nwm2.0-domain/data'
DOMAIN='/Volumes/ColdStorage/subsetter/domain-data/nwm.v3.0.11/domain'

# Run the docker container
docker run \
  -v $DOMAIN:/srv/domain \
  -v $OUTPUT:/srv/output \
  $IMAGE -510410.54170 1420079.71670 -497451.62760 1436986.49070 /srv/domain /srv/output 4 3.0.11

#Usage: entry.py [OPTIONS] YMIN XMIN YMAX XMAX [NWMV1_DATA] [OUTPUT_DIR]
#                 [CELL_BUFFER] [NWM_VERSION]:[1.2.4|2.0.0|3.0.11]
