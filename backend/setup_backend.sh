#!/bin/bash

BASEDIR=$(dirname "$0")

echo "[-] Setting up database for Rupture..."

read -p "[*] Please enter the name of the database (default: rupture): " DB_NAME
DB_NAME="${DB_NAME:-rupture}"
read -p "[*] Please enter the username for the database user (default: rupture): " DB_USER
DB_USER="${DB_USER:-rupture}"
read -p "[*] Please enter the password for the database user (default: random 0-9a-zA-Z): " DB_PASSWORD
DB_PASSWORD="${DB_PASSWORD:-$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)}"

$BASEDIR/env/bin/python $BASEDIR/setup_database.py --db_name $DB_NAME --db_user $DB_USER --db_password $DB_PASSWORD

read -p "[*] Create the database and user now? (y/n) " create_db
case $create_db in
    y|Y|yes|Yes|YES)
        echo "[*] Setup of the database requires access to MySQL server as root."
        mysql -u root -p < $BASEDIR/rupture.sql
        ;;
    *)
        ;;
esac

echo '[-] Applying Django migrations...'
if $BASEDIR/env/bin/python $BASEDIR/manage.py migrate; then
    echo '[*] Backend is ready for deployment.'
else
    echo "[!] Backend setup was interrupted."
fi
