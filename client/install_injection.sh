#!/bin/sh

command -v apt-get >/dev/null 2>&1 ||
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting.";
exit 1; }

#bettercap installation (requires rubygem)

sudo apt-get install ruby rubygems build-essential
sudo gem install syslog-logger #install syslog-logger from local directory or remote server
sudo apt-get install build-essential ruby-dev libpcap-dev #install dependencies

sudo gem install bettercap
