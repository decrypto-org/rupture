#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"

if [ -d $RUPTUREDIR ]; then
    CLIENTDIR="$RUPTUREDIR/client"
else
    CLIENTDIR=$BASEDIR
fi

REALTIMEURL=$1
VICTIMID=$2

echo "module.exports = {
    COMMAND_CONTROL_URL: '${REALTIMEURL}',
    VICTIM_ID: '${VICTIMID}'
};"  > $CLIENTDIR/config.js

cd $CLIENTDIR
if npm run webpack; then
    mkdir -p $CLIENTDIR/client_$VICTIMID
    cp -r $CLIENTDIR/test.html $CLIENTDIR/dist $CLIENTDIR/client_$VICTIMID
fi
