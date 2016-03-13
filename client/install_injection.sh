#!/bin/sh

command -v apt-get >/dev/null 2>&1 ||
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting.";
exit 1; }

#bettercap installation (requires rubygem)

apt-get install rubygems build-essential
gem install syslog-logger #install syslog-logger from local directory or remote server
apt-get install build-essential ruby-dev libpcap-dev #install dependencies

gem install bettercap
