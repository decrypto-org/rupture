[![Build
Status](https://travis-ci.org/dionyziz/rupture.svg?branch=develop)](https://travis-ci.org/dionyziz/rupture)

Rupture
=======
Rupture is a framework for easily conducting BREACH and other compression-based
attacks.

> For more information, please visit Rupture's home page: [RuptureIt](https://ruptureit.com)

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

Installation
============

You can install the whole framework as follows:

 - Install rupture.
```sh
rupture/ $ ./install.sh all
```

or you can also install each module separately, as below.

### Javascript

Rupture uses Javascript for communication between the client code and the realtime server. Client code is compiled using *babel* and server code is run on *Node.js*.

#### Injection
 - Install injection.
```sh
rupture$ ./install.sh injection
```

#### Client
 - Install client.
```sh
rupture$ ./install.sh client
```

### Python

Rupture uses Python for the Command & Control server. Communication between js realtime server and Python backend is performed with a Django API endpoint.

#### Backend
 - Install backend.
```sh
rupture/ $ ./install.sh backend
```

#### Sniffer
 - Install sniffer.
```sh
rupture/ $ ./install.sh sniffer
```

Execution
=========

#### Backend
 - Edit following configuration scripts:
    - rupture/backend/target_config.yml
    - rupture/backend/victim_config.yml
 - Setup backend.
```sh
rupture $ ./rupture setup
```
 - Deploy backend.
```sh
rupture $ ./rupture backend
```

#### Realtime
 - Deploy realtime.
```sh
rupture $ ./rupture realtime
```

#### Sniffer
 - Deploy sniffer.
```sh
rupture $ ./rupture sniffer
```

##### Attack
 - You can also deploy backend, realtime and sniffer modules all together:
```sh
rupture/ $ sudo ./rupture attack
```

**Note: Sniffer deployment - either standalone or all together with 'attack' - may need elevated privileges, since it requires access to network interface.**

#### Client
 - Client code is in following directory:
    - rupture/client/client_<id>

   where <id> is the victim's id in the backend database.
 - Open the following test HTML page in browser:
    - rupture/client/client_<id>/test.html

   or inject client code in HTTP responses:
```sh
rupture/client/client_<id> $ ./inject.sh
```
