#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

echo "[-] Populating targets..."
if $BASEDIR/env/bin/python $BASEDIR/populate_targets.py; then
    echo "[*] Targets have been set."
else
    echo "[!] Target setup was interrupted."
fi
