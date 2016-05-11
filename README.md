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

Development
===========

### Javascript

Rupture uses Javascript for communication between the client code and the realtime server. Client code is compiled using *browserify* and server code is run on *Node.js*.

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
 - Deploy client and injection.
```sh
rupture/client $ ./deploy.sh {victimIP} {realtimeURL} {VictimId}
```
example: ``` ./deploy.sh 192.168.1.2 http://localhost:3031 1 ```

 - Otherwise do it seperately.
   Build client.
```sh
rupture/client $ ./build.sh {realtimeURL} {VictimId}
```
 - Open test.html using browser or inject the js code to the victim's browser.
```sh
rupture/client $ ./inject {victimIP}
```



### Python

Rupture uses Python for the Command & Control server. Communication between js realtime server and Python backend is performed with a Django API endpoint.

#### Backend
 - Install backend.
```sh
rupture/ $ ./install.sh backend
```
 - Edit population script with the IP in which the backend runs or make your own popoulation script. The population script 'populate_ruptureit.py ' is in rupture/backend.
 - Deploy backend.
```sh
rupture/ $ ./deploy_backend.sh
```


#### Sniffer
 - Install sniffer.
```sh
rupture/ $ ./install.sh sniffer
```
 - Deploy sniffer.
```sh
rupture/ $ ./deploy_sniffer
```

##### You can also install and deploy the whole framework as it follows:

 - Install rupture.
```sh
rupture/ $ ./install.sh all
```
 - Edit the population script as mentioned above in the backend section.

 - Deploy rupture.
```sh
rupture/ $ sudo ./rupture.sh
```

