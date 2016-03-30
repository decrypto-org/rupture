#!/bin/bash

python='env/bin/python'

mkdir -p logs
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

echo '[-] Removing old database...'
rm -f db.sqlite3
if test -e "db.sqlite3"; then
    echo '[!] Database could not be deleted';
    exit;
fi

echo '[-] Applying Django migrations...'
$python manage.py migrate 2>&1 | tee logs/$log_file.log

echo '[-] Running test population scripts...'
$python populate_dionyziz.py 2>&1 | tee logs/$log_file.log

echo '[*] Backend has been deployed.'
$python manage.py runserver 2>&1 | tee logs/$log_file.log
