#!/bin/sh

REALTIMEURL=$1

echo "module.exports = {
    COMMAND_CONTROL_URL: '${REALTIMEURL}'
};" > config.js

gulp browserify
