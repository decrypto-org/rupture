![Rupture architecture](http://i.imgur.com/Q0oVChp.png)

### client <-> realtime ([socket.io](http://socket.io/))

Communication between client and realtime server is possible using [socket.io](http://socket.io/) websockets.

Client emits a message **get-work** requesting from the realtime server a specific work to be performed. Realtime server responds with a **do-work** message, passing a *work* object, that is structured as defined below:
```sh
typedef work
  amount: int
  url: string
  timeout: int (ms)
```

When the client has finished its work or has been interrupted due to network error, it emits a **work-completed** message, containing the following information:
```sh
{
  work: work,
  success: bool
}
```
*success* is *true* if all requests were performed correctly, otherwise it should return *false*.


### realtime -> backend (HTTP)

Realtime server communicates with the Python backend application, in order to populate information from client code and request the following attack steps. Backend implements various API endpoints for communication with the realtime server.

##### API

- /getwork
    - Requests from the server the next sample set of requests to perform as the victim.
    - Arguments:
        - victim: The id of the victim.
    - Returns *404 - Work not found* if there is an already ongoing sample collection. Otherwise, returns *200 - New work* with a JSON in the body, containing the work structure.
- /workcompleted
    - Indicates the successful or unsuccessful completion of work by the victim.
    - Arguments:
        - work: work
        - success: bool
    - If *success* is *True*, this indicates that the series of indicated requests were performed by the victim correctly. Otherwise, the victim failed to perform the required requests due to a network error or timeout.
