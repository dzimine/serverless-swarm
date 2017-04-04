#!/bin/bash
# Build a chain of Docker images

set -e

REGISTRY=${DOCKER_REGISTRY:-'pregistry:5000'}
echo "Using registry $REGISTRY"

# IMAGES=$(ls *.Dockerfile | awk -F . '{ print $1 }')
IMAGES=( Map Reduce Split )

echo ${IMAGES[@]}

for i in "${IMAGES[@]}"; do
  echo "Build image for $i ..."
  docker build -t "${i,,}" -t $REGISTRY/"${i,,}" -f $i.Dockerfile .
  echo "Pushing $i to local registry ..."
  docker push $REGISTRY/${i,,}
done