Rupture
=======
Rupture is a framework for easily conducting BREACH and other compression-based
attacks.

Authors
=======
Rupture is developed by:

* Dimitris Karakostas <dimit.karakostas@gmail.com>
* Dionysis Zindros <dionyziz@gmail.com>
* Eva Sarafianou <eva.sarafianou@gmail.com>

This research is being conducted at the [Cryptography & Security
lab](http://crypto.di.uoa.gr/) at the University of Athens and the National
Technical University of Athens.

License
=======
Rupture is licensed under MIT. See LICENSE for more information.

Development
===========

### Javascript

Rupture uses Javascript for communication between the client code and the realtime server. Client code is compiled using *browserify* and server code is run on *Node.js*.

#### Client
 - Install gulp on your system.
```sh
npm install -g gulp
```
 - Install required packages for compilation of the client code.
```sh
rupture/client $ npm install
```
 - Use browserify to compile the code.
```sh
rupture/client $ gulp browserify
```
 - Use watchify to automatically bundle together scripts compiled with browserify.
```sh
rupture/client $ gulp watchify
```
 - Open test.html using browser.

#### Realtime
 - Install Node.js on your system ([Instructions](https://nodejs.org/en/download/package-manager/)).
 - Install required packages for server setup.
```sh
rupture/realtime $ npm install
```
 - Start the server endpoint.
```sh
rupture/realtime $ npm start
```

### Python

Rupture uses Python for the Command & Control server. Communication between js realtime server and Python backend is performed with a Django API endpoint.

 - Install Python 2.7.x.
 - Install pip package manager.
 - Install virtual enviroment module using *pip*.
```sh
pip install virtualenv
```
 - Create Python virtual environment for the project.
```sh
rupture/backend $ virtualenv env
```
 - Activate virtual environment.
```sh
rupture/backend $ source env/bin/activate
```
 - Install package dependencies according to requirements.txt.
```sh
rupture/backend $ pip install -r requirements.txt
```
 - Migrate database.
```sh
rupture/backend $ python manage.py migrate
```
 - Run Django project.
```sh
rupture/backend $ python manage.py runserver
```
