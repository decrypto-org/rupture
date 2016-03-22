#!/bin/bash

mkdir -p logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Realtime has been deployed.'
npm start 2>&1 | tee logs/$log_file.log
