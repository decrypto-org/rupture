from mock import patch

from django.test import TestCase
from breach.sniffer import Sniffer


class SnifferTest(TestCase):
    def setUp(self):
        self.endpoint = 'http://localhost'
        sniffer_params = {
            'snifferendpoint': self.endpoint,
            'sourceip': '147.102.239.229',
            'host': 'dionyziz.com',
            'interface': 'wlan0',
            'port': '8080',
            'calibration_wait': 0.0
        }
        self.sniffer = Sniffer(sniffer_params)

    @patch('breach.sniffer.requests')
    def test_sniffer_start(self, requests):
        self.sniffer.start()
        self.assertTrue(requests.post.called)

    @patch('breach.sniffer.requests')
    def test_sniffer_read(self, requests):
        self.sniffer.read()
        self.assertTrue(requests.get.called)

    @patch('breach.sniffer.requests')
    def test_sniffer_delete(self, requests):
        self.sniffer.delete()
        self.assertTrue(requests.post.called)
