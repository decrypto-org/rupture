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


PARAMETER=$1

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

case $PARAMETER in
    "setup" ) setup;;
    "target" ) $BASEDIR/backend/setup_targets.sh;;
    "victim" ) $BASEDIR/backend/setup_victims.sh;;
    "backend" ) $BASEDIR/backend/deploy_backend.sh;;
    "sniffer" ) $BASEDIR/sniffer/deploy_sniffer.sh;;
    "realtime" ) $BASEDIR/realtime/deploy_realtime.sh;;
    "attack" ) attack;;
esac
