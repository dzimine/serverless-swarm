#!/bin/bash
#
ID=$(docker service ls | grep $1 | awk '{print $1}')
[ -z "$ID" ] && { echo "Service [$1] not found"; exit 1; }

echo "Service ID: $ID"
while true; do
	REPLICAS=$(docker service ls | grep $1 | awk '{print $4}');
	if [[ $REPLICAS == '1/1' ]]; then
		break;
	else
		echo "Waiting for $1 server to start... ";
		sleep 5;
	fi;
done
echo "Started!"