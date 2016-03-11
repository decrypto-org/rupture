#!/bin/sh

##PYTHON BACKEND INSTALLATION INSTRUCTIONS FOR DEBIAN, UBUNTU & LINUXMINT
##check if apt-get command exists. if not, abort.
command -v apt-get >/dev/null 2>&1 || 
{ echo >&2 "Installation script requires  apt-get but it's not installed.  Aborting."; 
exit 1; }



##install python (execute with elevated privileges)
sudo apt-get install -y python2.7

##install virtual enviroment module using pip.
sudo apt-get install -y python-pip
pip install virtualenv
virtualenv env #create Python virtual environment for the project

##Activate virtual environment
source env/bin/activate

##Install package dependencies
pip install -r requirements.txt

##Migrate database
python manage.py migrate

##Django project is ready to run!
