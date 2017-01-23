#!/bin/bash
# Build a chain of Docker images

set -e

REGISTRY=st2.my.dev:5000

docker build -t $REGISTRY/blast -f Dockerfile.blast .
docker build -t $REGISTRY/sb_base -f Dockerfile.sb_base .
docker build -t $REGISTRY/fgenesb -f Dockerfile.fgenesb .
docker build -t $REGISTRY/blast_prep -f Dockerfile.blast_prep .
docker build -t $REGISTRY/blast_fb -f Dockerfile.blast_fb .
docker build -t $REGISTRY/fgenesb_out -f Dockerfile.fgenesb_out .

# Push images to local registry
# docker images | grep $REGISTRY | awk '{ system("docker push " $1) }'