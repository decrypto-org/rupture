#!/bin/bash

function install_nodejs_npm {
    sudo apt-get install curl
    curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -   ## install or update nodejs with npm
    sudo apt-get install -y nodejs
    sudo apt-get install -y build-essential ##needed so as to be able to install native addons from npm
}

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
	install_nodejs_npm
	sudo npm install -g gulp
	(cd client
	npm install) ##install required packages for compilation of the client code
	;;
    injection)
	sudo apt-get install ruby rubygems build-essential
	sudo gem install syslog-logger #install syslog-logger from local directory or remote server
	sudo apt-get install build-essential ruby-dev libpcap-dev #install dependencies
	sudo gem install bettercap
	;;
    realtime)
	install_nodejs_npm
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
        install_nodejs_npm
        sudo npm install -g gulp
        (cd client
        npm install) ##install required packages for compilation of the client code
        sudo apt-get install ruby rubygems build-essential
        sudo gem install syslog-logger #install syslog-logger from local directory or remote server
        sudo apt-get install build-essential ruby-dev libpcap-dev #install dependencies
        sudo gem install bettercap
        (cd realitime
        npm install) ##install required packages for compilation of the client code
	 install_python
        (cd backend
        activate_virtualenv
        python manage.py migrate)
        (cd sniffer
        activate_virtualenv)
	 echo '##########################################################################'
	 echo "# Don't forget to create your population scripts or update existing ones #"
	 echo '##########################################################################'
	;;
  esac
done
