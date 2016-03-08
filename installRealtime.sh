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


#CLIENT

cd ./..
cd client

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

#PYTHON BACKEND

#install python
apt-get install -y python2.7

#install virtual enviroment module using pip.
apt-get install -y python-pip
pip install virtualenv
cd backend
virtualenv env #create Python virtual environment for the project

#Activate virtual environment
source env/bin/activate

#Install package dependencies
pip install -r requirements.txt

#Migrate database
python manage.py migrate

#Django project is ready to run!
