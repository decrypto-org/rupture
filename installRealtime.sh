#!/bin/sh

#REALTIME INSTALLATION INSTRACTIONS FOR DEBIAN, UBUNTU & LINUXMINT



# installing nodejs 
# source https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-an-ubuntu-14-04-server
apt-get install -y nodejs
apt-get install -y npm
npm install npm -g #update npm if already installed

#install required packages for server setups
cd ./..
cd realtime
npm install


