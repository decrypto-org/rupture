#!/bin/sh

#PYTHON BACKEND INSTALLATION INSTRACTIONS FOR DEBIAN, UBUNTU & LINUXMINT



#install python (execute with elevated privileges)
sudo apt-get install -y python2.7

#install virtual enviroment module using pip.
sudo apt-get install -y python-pip
pip install virtualenv
virtualenv env #create Python virtual environment for the project

#Activate virtual environment
source env/bin/activate

#Install package dependencies
pip install -r requirements.txt

#Migrate database
python manage.py migrate

#Django project is ready to run!
