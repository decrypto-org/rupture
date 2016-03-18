#!/bin/bash

mkdir -p logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[*] Sniffer has been deployed.'
env/bin/python sniff.py 2>&1 | tee logs/$log_file.log
