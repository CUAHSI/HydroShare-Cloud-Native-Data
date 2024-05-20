#!/bin/bash

if [ $# -eq 0 ]; then
	echo "No arguments supplied"
	echo "Must provide the tag for the docker image"
	echo
	echo "Usage: ./build-docker.sh <tag>"
	exit 1
fi

TAG=$1

docker build -f Dockerfile -t cuahsi/aorc-v1.1:$TAG .
