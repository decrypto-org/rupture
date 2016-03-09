#!/bin/sh

#CLIENT INSTALLATION INSTRUCTIONS FOR DEBIAN, UBUNTU & LINUXMINT


# installing nodejs 
# source https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-an-ubuntu-14-04-server
apt-get install -y nodejs npm
npm install -g npm #update npm if already installed

npm install -g gulp #install gulp on your system

#install required packages for compilation of the client code
npm install

#bettercap installation (requires rubygem)

#install rubygems, a package manager for Ruby
#source: http://www.cyberciti.biz/faq/debian-ubuntu-install-gem-the-frontend-to-rubygems/
apt-get install rubygems build-essential
gem install syslog-logger #install syslog-logger from local directory or remote server
apt-get install build-essential ruby-dev libpcap-dev #install dependecies

#install bettercap
gem install bettercap

#install ed gnu editor
apt-get install ed
