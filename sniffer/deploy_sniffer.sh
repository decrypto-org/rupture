#!/bin/bash

BASEDIR=$(dirname "$0")

mkdir -p $BASEDIR/logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Sniffer has been deployed.'
$BASEDIR/env/bin/python $BASEDIR/app.py 2>&1 | tee $BASEDIR/logs/$log_file.log
