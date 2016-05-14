#!/bin/bash

BASEDIR=$(dirname "$0")

echo "[-] Populating targets..."
if $BASEDIR/env/bin/python $BASEDIR/populate_targets.py; then
    echo "[*] Targets have been set."
else
    echo "[!] Target setup was interrupted."
fi
