#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"

if [ ! -d $RUPTUREDIR ]; then
    RUPTUREDIR=$BASEDIR
fi


echo "[-] Populating victims..."
if $BASEDIR/env/bin/python $BASEDIR/populate_victims.py $RUPTUREDIR/victim_config.yml; then
    echo "[*] Victims have been set."
else
    echo "[!] Victim setup was interrupted."
fi
