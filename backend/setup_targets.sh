#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"
if [ ! -d $RUPTUREDIR ]; then
    RUPTUREDIR=$BASEDIR
fi

echo "[-] Populating targets..."
if $BASEDIR/env/bin/python $BASEDIR/populate_targets.py; then
    echo "[*] Targets have been set."
else
    echo "[!] Target setup was interrupted."
fi
