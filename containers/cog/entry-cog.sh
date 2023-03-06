#!/bin/bash

usage() {
    echo Usage: 
    echo "  -i, --inputfile: path to input GeoTiff file"
    echo "  -o, --outputfile: path of the COG that will be generated"
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--inputfile)
      IF="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--outputfile)
      OF="$2"
      shift # past argument
      shift # past value
      ;;
    -h|--help)
	usage
	exit 0
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters


if [[ -z $IF ]] | [[ -z $OF ]]; then
    echo "Argument Error"
    echo "---------------------"
    echo " INPUT FILE   = ${IF}"
    echo " OUTPUT FILE  = ${OF}"
    echo "---------------------"
    usage
fi

gdal_translate -of COG -co COMPRESS=LZW $IF $OF

