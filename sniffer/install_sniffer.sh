#!/bin/bash

command -v apt-get >/dev/null 2>&1 ||
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting.";
exit 1; }


sudo apt-get install -y python2.7

sudo apt-get install -y python-pip
pip install virtualenv
virtualenv env

source env/bin/activate

pip install -r requirements.txt
