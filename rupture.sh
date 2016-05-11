#!/bin/bash -e

trap 'terminate' INT TERM QUIT

terminate() {
    trap '' INT TERM QUIT
    echo ""
    echo "[*] Shutting down..."
    kill 0
    wait
    echo "[*] Shut down complete."
}

BASEDIR=$(dirname "$0")
## Deploy different rupture modules in background processes
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

## Deploy backend
backend_python='backend/env/bin/python'

setup()
$backend_python backend/manage.py runserver &>> backend/logs/$log_file.log &
echo '[*] Backend has been deployed.'

## Deploy sniffer
sniffer_dir='sniffer'

mkdir -p $sniffer_dir/logs
$sniffer_dir/env/bin/python $sniffer_dir/sniff.py &> $sniffer_dir/logs/$log_file.log &
echo '[*] Sniffer has been deployed.'

## Deploy realtime
realtime_dir='realtime'

mkdir -p $realtime_dir/logs
node --harmony --harmony_destructuring $realtime_dir/index.js &> $realtime_dir/logs/$log_file.log &
echo '[*] Realtime has been deployed.'

echo ''
echo '[*] System has launched.'
echo ''

cat /dev/null > rupture.log
tailf rupture.log &

setup() {
    $BASEDIR/backend/setup_backend.sh
    $BASEDIR/backend/setup_targets.sh
    $BASEDIR/backend/setup_victims.sh
}
