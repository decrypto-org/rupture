#!/bin/bash

function install_python {
    sudo apt-get install -y python2.7
    sudo apt-get install -y python-pip
}


function activate_virtualenv {
    sudo pip install virtualenv
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
}

install_nvm_node() {
    if [ -z "$NVM_DIR" ]; then
        sudo apt-get install -y build-essential libssl-dev curl
        curl https://raw.githubusercontent.com/creationix/nvm/v0.33.2/install.sh | bash

        export NVM_DIR="$HOME/.nvm"
    fi
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm install 6.3
    nvm use 6.3
}

function error_checking() {
    for arg in "$@";
        do
            case $arg in
                injection|client|realtime|backend|sniffer|all) :;;
                *) return 1;;
            esac
        done
    return 0
}

install_bettercap() {
    sudo apt-get install build-essential ruby-dev libpcap-dev
    sudo gem install bettercap
}

USAGE="Usage: $0 options
options:
    client
    injection
    realtime
    backend
    sniffer
    all"

command -v apt-get >/dev/null 2>&1 ||
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting.";
exit 1; }

## no argument passed
if [ "$1" == "" ]
then
    echo "$USAGE"
    exit 0
fi

## Check all arguments for validation before beginning installation
error_checking $@
if [ $? == 1 ]
then
    echo "Invalid arguments"
    echo "$USAGE"
    exit 1
fi


for var in "$@"; do
    case "$var" in
    client)
        install_nvm_node
        (cd client
        npm install) ##install required packages for compilation of the client code
        ;;
    injection)
        install_bettercap
        ;;
    realtime)
        install_nvm_node
        (cd realtime
        npm install) ##install required packages for deploying the realtime server
        ;;
    backend)
        install_python
        (cd backend
        activate_virtualenv
        python manage.py migrate)
        ;;
    sniffer)
        install_python
        (cd sniffer
        activate_virtualenv)
        ;;
    all)
        install_nvm_node
        (cd client
        npm install)
        install_bettercap
        (cd realtime
        npm install)
        install_python
        (cd backend
        activate_virtualenv
        python manage.py migrate)
        (cd sniffer
        activate_virtualenv)
        echo '###########################################################################'
        echo "# Don't forget to create your configuration files or update existing ones #"
        echo '###########################################################################'
        ;;
  esac
done
