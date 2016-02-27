client <-> realtime (socket.io)
===================
typedef work
  amount: int
  url: string
  timeout: int (ms)

client -> realtime
  get-work
  work-completed
    {
      work: work
      success: bool
    }

realtime -> client
  do-work
    work: work

realtime -> backend (HTTP)
====================
/getwork
  Gets work. Requests from the server what is the next sample set of requests to perform as the victim.

  Args:
    victim

    The id of the victim.
    Returns 404 work not found if there is an already ongoing sample collection.
    Otherwise, returns 200 new work with a JSON in the body of type work.

/workcompleted
  Indicates the successful or unsuccessful completion of work by the victim.

  Args:
    work: work
    success: bool

    If success is true, this indicates that a the series of indicated requests were performed by the victim.
    Otherwise, the victim failed to perform the required requests due to a network error or timeout.
