#!/bin/bash 

SOURCEIP=$1
REALTIMEURL=$2

./build.sh ${REALTIMEURL}
./inject.sh ${SOURCEIP}
