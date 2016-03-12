import threading
from time import sleep


class Sniffer(threading.Thread):
    def __init__(self, arg):
        # Set thread to run as daemon
        self.daemon = True

        # Initialize object variables with parameters from arg dictionary
        self.arg = arg

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
