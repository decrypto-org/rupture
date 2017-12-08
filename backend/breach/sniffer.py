import requests
import logging
import json


logger = logging.getLogger(__name__)


class Sniffer(object):
    def __init__(self, params):
        self.endpoint = params['snifferendpoint']

        self.source_ip = params['sourceip']
        self.destination_host = params['host']
        self.interface = params['interface']
        self.destination_port = params['port']
        self.calibration_wait = params['calibration_wait']

    def get_sniffer_state(self):
        state = {
            'source_ip': self.source_ip,
            'destination_host': self.destination_host,
            'interface': self.interface,
            'destination_port': self.destination_port,
            'calibration_wait': self.calibration_wait
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
