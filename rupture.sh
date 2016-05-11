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


setup()
attack()

echo ''
echo '[*] System has launched.'
echo ''

setup() {
    $BASEDIR/backend/setup_backend.sh
    $BASEDIR/backend/setup_targets.sh
    $BASEDIR/backend/setup_victims.sh
}

attack() {
    echo "[*] Deploying Rupture..."
    $BASEDIR/backend/deploy_backend.sh &>/dev/null &
    $BASEDIR/sniffer/deploy_sniffer.sh &>/dev/null &
    $BASEDIR/realtime/deploy_realtime.sh &>/dev/null &
    echo "[*] Rupture is live."

    cat /dev/null > $BASEDIR/rupture.log
    tailf $BASEDIR/rupture.log
}
