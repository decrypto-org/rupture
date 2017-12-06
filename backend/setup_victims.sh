#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"
CLIENTDIR="$RUPTUREDIR/client"

if [ ! -d $RUPTUREDIR ]; then
    RUPTUREDIR=$BASEDIR
    CLIENTDIR="$(dirname -- $BASEDIR)/client"
fi


echo "[-] Populating victims..."
if $BASEDIR/env/bin/python $BASEDIR/populate_victims.py $RUPTUREDIR/victim_config.yml $CLIENTDIR; then
    echo "[*] Victims have been set."
else
    echo "[!] Victim setup was interrupted."
fi
