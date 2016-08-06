#!/bin/bash

HOMEDIR="/home/$usr"
BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOMEDIR/.rupture"

if [ -d $RUPTUREDIR ]; then
    REALTIMEDIR="$RUPTUREDIR/realtime"
else
    REALTIMEDIR=$BASEDIR
fi

mkdir -p $REALTIMEDIR/logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Realtime has been deployed.'
cd $REALTIMEDIR && npm start 2>&1 | tee logs/$log_file.log
