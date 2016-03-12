#!/bin/sh

##bettercap installation (requires rubygem)

##install rubygems, a package manager for Ruby
##source: http://www.cyberciti.biz/faq/debian-ubuntu-install-gem-the-frontend-to-rubygems/
apt-get install rubygems build-essential
gem install syslog-logger #install syslog-logger from local directory or remote server
apt-get install build-essential ruby-dev libpcap-dev #install dependecies

##install bettercap
gem install bettercap

