import threading
import socket
from scapy.all import sniff, Raw, IP, TCP, send


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

        # Initialize the captured packets' list to empty
        self.captured_packets = []

        # Thread has not come to life yet
        self.status = False

    def run(self):
        # Capture only response packets
        capture_filter = 'tcp and src host {} and dst host {}'.format(self.destination_ip, self.source_ip)

        self.status = True

        # Start blocking sniff function,
        # adding each sniffed packet in the 'captured_packets' list
        # and set it to stop when stop() is called
        sniff(iface=self.interface,
              filter=capture_filter,
              prn=lambda pkt: self.captured_packets.append(pkt),
              stop_filter=lambda pkt: not self.is_alive())

    def is_alive(self):
        # Return if thread is dead or alive
        return self.status

    def get_capture(self):
        return self.captured_packets

    def stop(self):
        # Kill it with fire!
        self.status = False

        self.stop_packet()

    def stop_packet(self):
        '''
        Send a dummy TCP packet to the victim with source IP the destination host's,
        which will be caught by sniff filter and cause sniff function to stop.
        '''
        send(IP(dst=self.source_ip, src=socket.gethostbyaddr(self.destination_host)[-1][0])/TCP(), verbose=0)
