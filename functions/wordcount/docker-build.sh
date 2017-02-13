#!/bin/bash
# Build a chain of Docker images

set -e


REGISTRY=st2.my.dev:5000

# IMAGES=$(ls *.Dockerfile | awk -F . '{ print $1 }')
IMAGES=( Map Reduce Split )

echo ${IMAGES[@]}

for i in "${IMAGES[@]}"; do
  echo "Build image for $i ..."
  docker build -t "${i,,}" -t $REGISTRY/"${i,,}" -f $i.Dockerfile .
  echo "Pushing $i to local registry ..."
  docker push $REGISTRY/${i,,}
done