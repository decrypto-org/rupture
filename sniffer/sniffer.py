import threading
import socket


class Sniffer(threading.Thread):
    def __init__(self, arg):
        super(Sniffer, self).__init__()

        # Set thread to run as daemon
        self.daemon = True

        # Initialize object variables with parameters from arg dictionary
        self.arg = arg
        try:
            self.interface = arg['interface']
            self.source_ip = arg['source_ip']
            self.destination_host = arg['destination_host']
        except KeyError:
            assert False, 'Invalid argument dictionary - Not enough parameters'

        try:
            self.destination_ip = socket.gethostbyaddr(self.destination_host)[-1][0]
        except socket.herror, err:
            assert False, 'socket.herror - ' + str(err)

        # If either of the parameters is None, assert error
        assert self.interface and self.source_ip and self.destination_host, 'Invalid argument dictionary - Invalid parameters'


        # Thread has not come to life yet
        self.status = False

    def run(self):
        self.status = True

        while self.is_alive():
           sleep(0.1)

    def is_alive(self):
        # Return if thread is dead or alive
        return self.status

    def stop(self):
        # Kill it with fire!
        self.status = False
