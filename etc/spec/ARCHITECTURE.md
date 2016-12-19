Rupture is a framework for conducting network attacks against web services. It
is focused on compression side-channel attacks, but provides a generalized
scalable system for performing any attack on web services which requires a
persistent command-and-control channel as well as attack adaptation. Suitable
attacks conductible by Rupture are the BREACH, CRIME, and POODLE attacks on
TLS. Rupture is suitable for any network chosen-plaintext attack.

Rupture was designed because all the available attack means to conduct BREACH,
CRIME, and POODLE attacks before Rupture were at the proof-of-concept level and
did not provide a productized robust system that can work in real conditions.
As researchers, we spent a lot of time building separate proof-of-concept
implementations of BREACH and invested a lot of time to mount attacks against
specific end-points. Our motivation was that it takes a lot of effort to
conduct such an attack without the appropriate tools.

With Rupture, our aim was to make it easier to mount such attacks and provide
reasonable pre-configured defaults, targets, and attack strategies that can be
used in practice or modified to suit the need of new attacks. The framework is
designed specifically to allow for further investigations on both the practical
and theoretical side. On the practical side, our network sniffing and injection
components are modular and replaceable. On the theoretical side, our analysis
and strategy core is independent of data collection means, allowing theoretical
cryptographers to verify or reject statistical analysis hypotheses through
experimental adaptive sample collection.

This document describes the architectural design decisions behind Rupture and
their merit. It is a recommended reading if you plan to contribute to Rupture
or implement novel attacks.

# Overview

An overview of the Rupture architecture is shown in Figure 1.

![Rupture architecture](http://i.imgur.com/Q0oVChp.png)

***Figure 1: The Rupture architecture***

Rupture is a service-based architecture system which contains multiple
independent components. While the components are designed to be able to run
independently on different networks or computer systems, easy instances of the
attack can be performed by running all subsystems on an individual system. We
provide appropriate scripts to conduct such attacks easily.

The attack framework assumes a **target** service to be attacked. Typically
this target service is a web service which uses TLS. Specifically, we are
targeting services that provide HTTPS end-points. However, this assumption can
be relaxed and attacks against other similar protocols are possible. Any
protocol that exchanges encrypted data on the network and for which a
theoretical attack exists can in principle be attacked using Rupture. We
designed Rupture to be a good playground for experimentation for such new
attacks. Examples of other encrypted protocols for which attacks can be tested
include SMTP and XMPP.

The attack also assumes a user of the target service for which data will be
decrypted, the **victim**. The victim is associated with a particular target.

There are two underlying assumptions in our attack: The injection and the
sniffing assumptions. These are often achieved through the same means, although
not necessarily.

The injection assumption states that the adversary is able to
inject code to the victim's machine for execution. This code is able to issue
adaptive requests to the target service. Injection in Rupture is achieved
through the **injector** component. The code that is injected is the **client**
component.

The sniffing assumption states that the adversary is able to observe network
traffic between the victim and the target. This traffic is typically
ciphertexts. Sniffing is achieved through the **sniffer** component.

The client must issue adaptive requests. For this purpose, it receives commands
through a **command-and-control** channel. These commands are sent to the
client from the **real-time** component to which the client maintains a
persistent connection.

The real-time component is only responsible for communicating with the client.
The real decisions for the attack are driven by the **back-end**, which
maintains a persistent attack state. The back-end stores persistent data in a
SQLite **database** and receives data from the sniffer to perform analyses.

The various components are described in detail in the next sections.

# Principles of attack

The attack takes place by first injecting client code into the victim's
computer using the injector. The client then opens a command-and-control
channel to the real-time service, which forwards work from the backend to the
client.

When a client associated with a victim asks to work, the backend passes a work
request to the real-time service, which passes it to the client. These work
requests ask the client to perform a series of network requests from the
victim's computer to the target web app. As these requests are made from the
victim's browser, they contain authentication cookies which authenticate the
user to the target service. As such, the responses contain sensitive data, but
that data is not readable by the client due to same-origin policy.

When a response arrives from the target web app to the victim's computer, the
encrypted response is collected by the sniffer on the network. The encrypted
data pertaining to one response is a **sample**. Each work request asks for
multiple requests to be made, and therefore multiple samples are collected per
work request. The set of samples collected for a particular work request are a
**sampleset**.

A successful attack completely decrypts a portion of the plaintext. The portion
of the plaintext which the attack tries to decrypt is the **secret**. That
portion is identified through an initially known prefix which distinguishes it
from other secrets. This prefix is typically 3 to 5 bytes long. Each byte of
the secret can be drawn from a given **alphabet**, the secret's alphabet. For
example, some secrets only contain numbers, and so their alphabet is the set of
numbers [0-9].

At each stage of the attack, a prefix of the secret is known, because that
portion of the secret has already been successfully decrypted. The prefix
decrypted grows until the whole secret becomes known, at which stage the attack
is completed.

When a certain prefix of the secret is known, the next byte of the secret must
be determined. The attack initially assumes the next unknown byte of the secret
can come from the secret's alphabet, but slowly drills down and rejects
alphabet symbols until only one candidate symbol remains. At each stage of the
attack of one byte of the secret, there is a certain **known alphabet** which
the next byte can take. This known alphabet is a subset of the secret's
alphabet.

To drill down on the known alphabet, one of two methods is employed. In the
**serial method**, each symbol of the known alphabet is tried sequentially. In
the **divide & conquer method**, the alphabet is split into two **candidate
alphabet** subsets which are tried independently.

The attack is conducted in **rounds**. In each round, a decision is made
about the state of the attack and more becomes known about the secret. In a
round, either the next byte of the secret becomes known, or the known alphabet
is drilled down to a smaller set. In order to compare various different
candidate alphabets, the attack executes a series of **batches** of data
collection for each round.

In each batch, several samples are collected from each probability distribution
pertaining to a candidate alphabet, forming a sampleset. When samplesets of the
same amount of samples each have been collected for all the candidate
alphabets, a batch is completed and the data is analyzed. The analysis is
performed by the **analyzer** which statistically compares the samples of
different distributions and decides which distribution is optimal, i.e.
contains the correct guess. This decision is made with some **confidence**,
which is expressed in bytes. If the confidence is insufficient, an additional
batch of samplesets is collected, and the analysis is redone until the
confidence value surpases a given threshold.

Once enough batches have been collected for a decision to be made with good
confidence, the round of the attack is completed and more information about the
secret becomes known. Each round at best collects one bit of information of the
secret.

# Injector

The injector component is responsible for injecting code to the victim's
computer for execution. In our implementation, we assume the adversary controls
some network of the victim. Our injector injects the client code in all
unauthenticated HTTP responses that the victim receives. This Javascript code
is then executed by the victim's browser in the context of the respective
domain name. We use [bettercap](https://www.bettercap.org/) to perform the HTTP
injection. The injection is performed by ARP spoofing the local network and
forwarding all traffic in a Man-in-the-Middle manner. It is simply a series of
shell scripts that use the appropriate bettercap modules to perform the attack.

As all HTTP responses are infected, this provides for greatly increased
robustness. The injected client code remains dormant until it is asked to wake
up by the command-and-control channel. This means that the user can switch
between browsers, reboot their computer, close and reopen browser tabs, and the
attack will keep running.

The injector component needs to run on the victim's network and as such is
light-weight and stateless. It can be easily deployed on a machine such as a
Raspberry Pi, and can be used for massive attacks, for example at public
unencrypted networks such as coffee shops or airports. Multiple injectors can
be deployed to different networks, all controlled by the same central
command-and-control channel.

While injection is performed on the local network through altering HTTP
responses in our case, the injector component is independent and can be
replaced by alternative means. Other good points of injection that can be used
instead of our build-in injector are giving a link directly to the victim, in
which case attack robustness is limited, or by injecting code at the ISP or
router level if the adversary has such a level of access.

# Sniffer

The sniffer component is responsible for collecting data directly from the
victim's network. As the client issues chosen plaintext requests, the sniffer
collects the respective ciphertext requests and ciphertext responses as they
travel on the network. These encrypted data are then transmitted to the backend
for further analysis and decryption.

Our sniffer implementation runs on the same network as the victim. It is a
Python program which uses [scapy](http://www.secdev.org/projects/scapy/) to
collect network data.

Our sniffer runs on the same machine as our injector and utilizes the
injector's ARP spoofing to retrieve the data from the wire or the air. If you
are not using our injector, you can still use our sniffer by feeding it packets
from the network, for example by using arpspoof directly.

Other sniffer alternatives include sniffing data on the target network side, or
on the ISP or router point if the adversary has such a level of access.

The sniffer exposes an HTTP API which is utilized by the backend for
controlling when sniffing starts, when it is completed, and to retrieve the
data that was sniffed. This API is described below.

## backend <-> sniffer (HTTP)

The Python backend application communicates with the sniffer server, in order
to initiate a new sniffer, get information or delete an existing one. The
sniffer server implements a RESTful API for communication with the backend.

### /start

POST request that initializes a new sniffer. Upon receiving this request, the
sniffer service should start sniffing.

The request contains a JSON with the following fields:

- source_ip: The IP of the victim on the local network.
- destination_host: The hostname of the target that is being attacked.

Returns HTTP `201` if the sniffer is created correctly. Otherwise, it returns
HTTP `400` if either of the parameters is not properly set, or HTTP `409 -
Conflict`, if a sniffer for the given arguments already exists.

### /read

GET request that asks for the network capture of the sniffer.

The GET parameters are:

- source_ip: The IP of the victim on the local network.
- destination_host: The hostname of the target that is being attacked.

Returns HTTP `200` with a JSON that has a field *capture*, which contains the
network capture of the sniffer as hexadecimal digits, and a field *records*,
that contains the total amount of captured TLS application records. In case of
error, HTTP `422 - Unprocessable Entity` is returned if the captured TLS
records were not properly formed on the sniffed network, or HTTP `404` if no
sniffer with the given parameters exists.

### /delete

POST request that asks for the deletion of the sniffer.

The request contains a JSON with the following fields:

- source_ip: The IP of the victim on the local network.
- destination_host: The hostname of the target that is being attacked.

Returns HTTP `200` if the sniffer was deleted successfully, or HTTP `404` if no
sniffer with the given parameters exists.

# Client

The client runs on the victim machine and is responsible for issuing adaptive
chosen plaintext requests to the target oracle.

The client is written in Javascript and runs in a different context from the
target website. Thus, it is subject to [same-origin
policy](https://en.wikipedia.org/wiki/Same-origin_policy) and cannot read the
plaintext or encrypted responses. However, the encrypted requests and responses
are available to the sniffer through direct network access.

The client contains minimal logic. It connects to the real-time service through
a command-and-control channel and registers itself there. Afterwards, it waits
for work instructions by the command-and-control channel, which it executes.
The client does not take any decisions or receive data about the progress of
the attack other than the work it is requested to do. This is intentional so as
to conceal the workings of the adversary analysis mechanisms from the victim in
case the victim attempts to reverse engineer what the adversary is doing.
Furthermore, it allows the system to be upgraded without having to deploy a new
client at the victim's network, which can be a difficult process.

As a regular user is browsing the Internet, multiple clients will be injected
in insecure pages and they will run under various contexts. All of them will
register and maintain an open connection through a command-and-control channel
with the real-time service. The real-time service will enable one of them for
this victim, while keeping the others dormant. The one enabled will then
receive work instructions to perform the required requests. If the enabled
client dies for whatever reason, such as a closed tab, one of the rest of the
clients will be waken up to take over the attack.

The client is a Javascript program written using harmony / ECMAScript 6 and
compiled using gulp and browserify.

# Real-time

The real-time service is a service which awaits for work requests by clients.
It can handle multiple targets and victims. It receives command-and-control
connections from various clients which can live on different networks,
orchestrates them, and tells them which ones will remain dormant and which ones
will receive work, enabling one client per victim.

The real-time service is developed in Node.js.

The real-time service maintains open web socket command-and-control connections
with clients and connects to the backend service, facilitating the
communication between the two.

The real-time server forwards work requests and responses between the client
and the Django service. The communication it does with the client uses web
sockets in order to achieve bi-directional communication in real-time. This
also facilitates the ability to detect that a client has gone away, which is
registered as a failure to do work. This can happen for example due to network
errors if the victim disconnects from the network, closes their tab or browser,
and so on. It is imperative that incomplete work is marked as failed as soon as
possible so that the attack can continue by recollecting the failed samples.

The web socket API exposed by the real-time service is explained below.

## client <-> real-time protocol

The client / real-time protocol is implemented using
[socket.io](http://socket.io/) websockets.

### client-hello / server-hello

When the client initially connects to the real-time server, it sends the message
**client-hello** passing its *victim_id* to the real-time server.  The server
responds with a **server-hello** message. After these handshake messages are
exchanged, the client and server can exchange futher messages.

### get-work / do-work

When the client is ready to perform work, it emits the message **get-work**
requesting work to be performed from the real-time server. The real-time server
responds with a **do-work** message, passing a *work* object, that is
structured as defined below:

```sh
typedef work
  amount: int
  url: string
  timeout: int (ms)
```

If the real-time service is unable to retrieve work from the backend due to a
communication error, real-time will return an empty work object indicating
there is no available work to be performed at this time.

### work-completed

When the client has finished its work or has been interrupted due to network
error, it emits a **work-completed** message, containing the following
information:

```sh
{
  work: work,
  success: bool
}
```

*success* is *true* if all requests were performed correctly, otherwise it
is *false*. *work* contains the work that was performed or failed to perform.

# Backend

The backend is responsible for strategic decision taking, statistical analysis
of samples collected, adaptively advancing the attack, and storing persistent
data about the attacks in progress for future analysis.

The backend talks to the real-time service for pushing work out to clients. It
also speaks to the sniffer for data collection.

It is implemented in Python using the Django framework.

The backend exposes a RESTful API via HTTP to which the real-time service
makes requests for work. This API is explained below.

## real-time -> backend (HTTP)

The backend implements various API endpoints for communication with the
real-time server.

### `/get_work/<victim>`

HTTP GET endpoint. Requests work to be performed on behalf of a client.

Arguments:

- victim: The id of the victim.

If there is work to be done, it returns an HTTP `200` response with the JSON
body containing the work structure. The work will contain instructions to
collect multiple samples from the same distribution by performing a series of
similar requests. The samples associated with a particular work request and
performed all together constitute a **sampleset**.

In case no work is available for the client, it returns an HTTP `404` response.
Work can be unavailable in case a different client is already collecting data
for the particular victim, and we do not wish to interfere with it.

### `/work_completed/<victim>`

HTTP POST endpoint.

Indicates on behalf of the client that some work was successfully or
unsuccessfully completed.

Arguments:

- work: work
- success: bool

If *success* is *True*, this indicates that the series of indicated requests
were performed by the victim correctly. Otherwise, the victim failed to perform
the required requests due to a network error or a timeout and the work has to
be redone.

The backend also exposes a RESTful API via HTTP to which the the Web UI
makes requests for work. This API is explained below.

## webUI <-> backend(HTTP)

The backend implements various API endpoints for communication with the
Web UI.

### `/victim`

HTTP POST and GET endpoint.

On a POST request, it creates a new victim.

Arguments:

- IP: IP address
- target: string

Returns HTTP `200` with a JSON that has a field *victimid*, which contains the
ID of the new victim.

On a GET request, it asks for  all the stored victims that the attack is still
running on, has been paused or has been completed.

No arguments

Returns HTTP 200 with a JSON that contains a list of all the stored
victims.

### `/attack`

HTTP POST endpoint. It launches an attack.

There are two conditions:

1) The victim already exists

Arguments:

- victim_id: The id of the victim
- target: string

2) The victim doesn't exist

Arguments:

- sourceip: IP address
- target: string

Before launching, the attack, the victim is created

Returns HTTP `200` with a JSON that has a field *victimid*, which contains the
ID of the victim.

### `/victim/<victim_id>`

HTTP GET, PUT and DELETE endpoint.

On a GET request, it asks for the general information and details
for the attack to the victim with the specific victimId.

Arguments:

- victim_id: The id of the victim

Returns HTTP `200` with a JSON with the details for the specific victim.

On a PUT request, it passes the desired state of the attack ("paused" or "running")
and the victim_id and asks the backend to update the attack state of the victim
with the specific victim_id, i.e pause or resume running the attack.

Arguments:

- victim_id: The id of the victim
- state: string (either "running" or "paused")

Returns HTTP 200.

On a DELETE request, the backend deletes the victim with the specific victim_id

Arguments:

- victim_id: The id of the victim

Returns HTTP 200.

### `/victim/not_started`

HTTP GET endpoint.

On a GET request, it asks for all possible victims to attack.

No arguments.

Returns HTTP 200 with a JSON with a list of possible victims' IPs
and machine names.

### `/target`

HTTP POST and GET endpoint.

On a POST request, it creates a new target.

Arguments:

- name: The target's name
- endpoint: The target's endpoint
- prefix: The know prefix of the secret
- secretlength: The secret's length
- alphabet: The secret's alphabet
- alignmentalphabet: The alignment alphabet
- recordscardinality: The records' cardinality
- method: The method of the attack, serial or divide & conquer

Returns HTTP 200 with a JSON with the target's name.

On a GET request, it asks for the targets for which the attack is possible.

No arguments.

Returns HTTP `200` with a JSON with a list of possible targets
and machine names.
