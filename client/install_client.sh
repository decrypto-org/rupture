#!/bin/sh

##CLIENT INSTALLATION INSTRUCTIONS FOR DEBIAN, UBUNTU & LINUXMINT
##check if apt-get command is installed
command -v apt-get >/dev/null 2>&1 || 
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting."; 
exit 1; }

## installing nodejs 
## source https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-an-ubuntu-14-04-server
apt-get install -y nodejs npm
npm install -g npm ##update npm if already installed

npm install -g gulp ##install gulp on your system

##install required packages for compilation of the client code
npm install

