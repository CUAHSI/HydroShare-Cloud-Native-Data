#!/bin/bash

function run_simulation () {
    docker run --rm -ti \
        -v $1:/ngen/data \
        --entrypoint=/bin/bash \
	cuahsi/ngiab:v0.1
}

#
## /dmod/bin/ngen-serial <catchment_data_path> all <nexus_data_path> all <realization_config_path>
#
##/dmod/bin/ngen-serial /ngen/ngen/data/catchments.geojson all /ngen/ngen/data/nexus.geojson all /ngen/ngen/data/config/realization.json
#

unset -v LOCAL_INPUT_DIR
unset -v LOCAL_OUTPUT_DIR
USE_ABSOLUTE_PATHS='false'


print_usage() {
   echo "*** NGIAB Executor ***"
   echo ""
   echo "usage: $0 -i                   # local path to input directory"
   echo "       $0 -o         		# local path to output directory"
   echo "       $0 -h 		 	# show this screen"
   echo "***"
}

if [ $# -eq 0 ] ; then
    print_usage
    exit 1
fi

while getopts 'i:o:hv' flag; do
  case "${flag}" in
    i) LOCAL_INPUT_DIR="${OPTARG}" ;;
    o) LOCAL_OUTPUT_DIR="${OPTARG}" ;;
    a) USE_ABSOLUTE_PATHS='true' ;;
    h) print_usage
       exit 1 ;;
    v) verbose='true' ;;
    *) print_usage
       exit 1 ;;
  esac
done

shift "$(( OPTIND - 1 ))"

#if [ -z "$LOCAL_INPUT_DIR" ] || [ -z "$LOCAL_OUTPUT_DIR" ]; then
if [ -z "$LOCAL_INPUT_DIR" ]; then 
    #echo 'Must provide both `Input` and `Output` directories -- (flags -i and -o)' >&2
    echo 'Must provide `Input` directory -- (flag -i)' >&2
        exit 1
fi

# convert relative paths to absolute paths
if [ "$USE_ABSOLUTE_PATHS" = false ] ; then
    LOCAL_INPUT_DIR=$(realpath "$LOCAL_INPUT_DIR")
#    LOCAL_OUTPUT_DIR=$(realpath "$LOCAL_OUTPUT_DIR")
fi

# check that these directories exist before moving on
DIRS_EXIST='true'
if [ ! -d "$LOCAL_INPUT_DIR" ]; then 
    echo "Directory does not exist: $LOCAL_INPUT_DIR"
    DIRS_EXIST='false'
fi
#if [ ! -d "$LOCAL_OUTPUT_DIR" ]; then 
#    echo "Directory does not exist: $LOCAL_OUTPUT_DIR"
#    DIRS_EXIST='false'
#fi
if [ "$DIRS_EXIST" = false ] ; then
    exit 1
fi

# invoke the simulation
run_simulation $LOCAL_INPUT_DIR

exit 0
