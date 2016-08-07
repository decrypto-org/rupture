#!/bin/bash

BASEDIR=$(dirname "$0")

mkdir -p $BASEDIR/logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Backend has been deployed.'
$BASEDIR/env/bin/python $BASEDIR/manage.py runserver 2>&1 | tee $BASEDIR/logs/$log_file.log
