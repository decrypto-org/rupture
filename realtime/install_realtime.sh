#!/bin/sh

command -v apt-get >/dev/null 2>&1 || 
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting."; 
exit 1; }


sudo apt-get install -y nodejs npm
npm install -g npm #update npm if already installed

##install required packages for server setups
npm install


