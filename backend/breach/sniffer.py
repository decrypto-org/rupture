import requests
import logging
import json
from time import sleep


logger = logging.getLogger(__name__)


class Sniffer(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def start(self, source_ip, destination_host):
        logger.debug('Making post request')
        r = requests.post(
            '%s/start' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'source_ip': source_ip,
                'destination_host': destination_host
            })
        )
        logger.debug('Post request completed')
        r.raise_for_status()
        logger.debug('No raise for status')

    def read(self, source_ip, destination_host):
        r = requests.get(
            '%s/read' % self.endpoint,
            params={
                'source_ip': source_ip,
                'destination_host': destination_host
            }
        )
        r.raise_for_status()
        return r.json()

    def delete(self, source_ip, destination_host):
        r = requests.post(
            '%s/delete' % self.endpoint,
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'source_ip': source_ip,
                'destination_host': destination_host
            })
        )
        r.raise_for_status()

if __name__ == '__main__':
    source_ip = '147.102.239.229'
    destination_host = 'dionyziz.com'
    print('Initializing sniffer')
    sniffer = Sniffer('http://%s:9000' % source_ip)
    print('Starting')
    sniffer.start(source_ip, destination_host)
    print('Sniff started')
    sleep(5)
    print('Reading sniffer data')
    data = sniffer.read(source_ip, destination_host)
    print('Sniffer data read:\n%s', data)
    print('Stopping sniffer')
    sniffer.stop(source_ip, destination_host)
    print('Sniffer stopped')
