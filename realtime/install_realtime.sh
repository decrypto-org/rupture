#!/bin/sh

command -v apt-get >/dev/null 2>&1 ||
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting.";
exit 1; }


sudo apt-get install -y nodejs npm
sudo npm install -g npm #update npm if already installed
sudo ln -s /usr/bin/nodejs /usr/bin/node ##update nodejs if already installed
sudo npm cache clean -f
sudo npm install -g n
sudo n stable

##install required packages for server setups
npm install
