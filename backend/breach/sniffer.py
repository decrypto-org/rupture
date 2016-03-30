import requests
import logging
import json
from time import sleep


logger = logging.getLogger(__name__)


class Sniffer(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def start(self, source_ip, destination_host, interface, destination_port):
        logger.debug('Making post request')
        r = requests.post(
            '%s/start' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'source_ip': source_ip,
                'destination_host': destination_host,
                'interface': interface,
                'destination_port': destination_port
            })
        )
        logger.debug('Post request completed')
        r.raise_for_status()
        logger.debug('No raise for status')

    def read(self, source_ip, destination_host, interface, destination_port):
        r = requests.get(
            '%s/read' % self.endpoint,
            params={
                'source_ip': source_ip,
                'destination_host': destination_host,
                'interface': interface,
                'destination_port': destination_port
            }
        )
        r.raise_for_status()
        return r.json()

    def delete(self, source_ip, destination_host, interface, destination_port):
        r = requests.post(
            '%s/delete' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'source_ip': source_ip,
                'destination_host': destination_host,
                'interface': interface,
                'destination_port': destination_port
            })
        )
        r.raise_for_status()

if __name__ == '__main__':
    source_ip = '147.102.239.229'
    destination_host = 'dionyziz.com'
    interface = 'wlan0'
    destination_port = '443'
    print('Initializing sniffer')
    sniffer = Sniffer('http://%s:9000' % source_ip)
    print('Starting')
    sniffer.start(source_ip, destination_host, interface, destination_port)
    print('Sniff started')
    sleep(5)
    print('Reading sniffer data')
    data = sniffer.read(source_ip, destination_host, interface, destination_port)
    print('Sniffer data read:\n%s', data)
    print('Stopping sniffer')
    sniffer.stop(source_ip, destination_host, interface, destination_port)
    print('Sniffer stopped')
