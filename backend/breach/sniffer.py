import requests
import logging
import json
from time import sleep


logger = logging.getLogger(__name__)


class Sniffer(object):
    def __init__(self, endpoint, source_ip, destination_host, interface, destination_port):
        self.endpoint = endpoint
        self.source_ip = source_ip
        self.destination_host = destination_host
        self.interface = interface
        self.destination_port = destination_port

    def get_sniffer_state(self):
        state = {
            'source_ip': self.source_ip,
            'destination_host': self.destination_host,
            'interface': self.interface,
            'destination_port': self.destination_port
        }
        return state

    def start(self):
        logger.debug('Making post request')
        r = requests.post(
            '%s/start' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps(self.get_sniffer_state())
        )
        logger.debug('Post request completed')
        r.raise_for_status()
        logger.debug('No raise for status')

    def read(self):
        r = requests.get(
            '%s/read' % self.endpoint,
            params=self.get_sniffer_state()
        )
        r.raise_for_status()
        return r.json()

    def delete(self):
        r = requests.post(
            '%s/delete' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps(self.get_sniffer_state())
        )
        r.raise_for_status()

if __name__ == '__main__':
    source_ip = '147.102.239.229'
    destination_host = 'dionyziz.com'
    interface = 'wlan0'
    destination_port = '443'
    print('Initializing sniffer')
    sniffer = Sniffer('http://%s:9000' % source_ip, source_ip, destination_host, interface, destination_port)
    print('Starting')
    sniffer.start()
    print('Sniff started')
    sleep(5)
    print('Reading sniffer data')
    data = sniffer.read()
    print('Sniffer data read:\n%s', data)
    print('Stopping sniffer')
    sniffer.stop()
    print('Sniffer stopped')
