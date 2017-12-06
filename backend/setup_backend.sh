#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")
RUPTUREDIR="$HOME/.rupture"

echo '[-] Flushing old database, if exists...'
$BASEDIR/env/bin/python $BASEDIR/manage.py flush --no-input

if [ -d $RUPTUREDIR ]; then
    echo "[-] Using Rupture directory in $RUPTUREDIR..."
    mkdir -p $RUPTUREDIR/backend

    echo "[-] Copying configuration files to config directory..."
    cp $BASEDIR/victim_config.yml $RUPTUREDIR/victim_config.yml
    cp $BASEDIR/target_config.yml $RUPTUREDIR/target_config.yml
else
    RUPTUREDIR=$BASEDIR
fi

echo '[-] Applying Django migrations...'
if $BASEDIR/env/bin/python $BASEDIR/manage.py migrate; then
    echo '[*] Backend is ready for deployment.'
else
    echo "[!] Backend setup was interrupted."
fi
