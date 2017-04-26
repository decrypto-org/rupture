#!/bin/sh

#SOURCEIP = "$1"
#REALTIMEURL = "$2"

#edit breach.jsx add REALTIMEURL constant

gulp browserify

./runner.sh "$1"
