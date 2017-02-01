#!/bin/bash

BASEDIR=$(dirname "$0")

echo '[-] Flushing old database, if exists...'
$BASEDIR/env/bin/python $BASEDIR/manage.py flush --no-input

echo '[-] Applying Django migrations...'
if $BASEDIR/env/bin/python $BASEDIR/manage.py migrate; then
    echo '[*] Backend is ready for deployment.'
else
    echo "[!] Backend setup was interrupted."
fi
