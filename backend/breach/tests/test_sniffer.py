from mock import patch

from django.test import TestCase
from breach.sniffer import Sniffer


class SnifferTest(TestCase):
    def setUp(self):
        self.endpoint = 'http://localhost'
        self.sniffer = Sniffer(self.endpoint, '147.102.239.229', 'dionyziz.com', 'wlan0', '8080')

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
