#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

mkdir -p $BASEDIR/logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Realtime has been deployed.'
cd $BASEDIR && npm start 2>&1 | tee logs/$log_file.log
