#!/bin/bash -e

## Deploy different rupture modules in background processes
log_file=$(date "+%Y_%m_%d-%H_%M_%S")

## Deploy backend
backend_dir='backend'
backend_python='$backend_dir/env/bin/python'

mkdir -p $backend_dir/logs
echo '[-] Removing old database...'
rm -f $backend_dir/db.sqlite3
echo '[-] Applying Django migrations...'
$backend_python $backend_dir/manage.py migrate &>> $backend_dir/logs/$log_file.log
echo '[-] Running test population scripts...'
$backend_python $backend_dir/populate_dimkarakostas.py &>> $backend_dir/logs/$log_file.log
$backend_python $backend_dir/manage.py runserver &>> $backend_dir/logs/$log_file.log &
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


## Trap Ctrl-C signal and kill all subtree of current process
trap "kill -- -$(ps -o pgid= $PID | grep -o [0-9]*)" SIGINT

wait
