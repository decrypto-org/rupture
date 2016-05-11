#!/bin/bash

BASEDIR=$(dirname "$0")

echo '[-] Removing old database, if exists...'
rm -f $BASEDIR/db.sqlite3
if test -e "$BASEDIR/db.sqlite3"; then
    echo "[!] Database could not be deleted. Check permissions on $BASEDIR/db.sqlite3?";
    exit;
fi

echo '[-] Applying Django migrations...'
if $BASEDIR/env/bin/python $BASEDIR/manage.py migrate; then
    echo '[*] Backend is ready for deployment.'
else
    echo "[!] Backend setup was interrupted."
fi
