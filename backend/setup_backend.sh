#!/bin/bash

BASEDIR=$(dirname "$0")

echo "[*] Setup of the database requires access to MySQL server as root."
mysql -u root -p < $BASEDIR/init.sql

echo '[-] Applying Django migrations...'
if $BASEDIR/env/bin/python $BASEDIR/manage.py migrate; then
    echo '[*] Backend is ready for deployment.'
else
    echo "[!] Backend setup was interrupted."
fi
