#!/bin/bash
# Build a chain of Docker images

set -e


REGISTRY=st2.my.dev:5000

# Order matters, so don't be too smart :)
#    IMAGES=$(ls Dockerfile.* | awk -F . '{ print $NF }')
IMAGES=( blast sb_base fgenesb blast_prep blast_fb fgenesb_out )

echo ${IMAGES[@]}

for i in "${IMAGES[@]}"; do
  echo "Build image for $i ..."
  docker build -t sb/$i -t $REGISTRY/$i -f Dockerfile.$i .
  echo "Pushing $i to local registry ..."
  docker push $REGISTRY/$i
done
