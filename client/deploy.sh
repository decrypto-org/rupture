#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"

if [ -d $RUPTUREDIR ]; then
    CLIENTDIR="$RUPTUREDIR/client"
else
    CLIENTDIR=$BASEDIR
fi

SOURCEIP=$1
REALTIMEURL=$2
VICTIMID=$3

$CLIENTDIR/build.sh ${REALTIMEURL} ${VICTIMID}
$CLIENTDIR/inject.sh ${SOURCEIP}
