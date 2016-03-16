from mock import patch

from django.test import TestCase
from breach.sniffer import Sniffer


class SnifferTest(TestCase):
    def setUp(self):
        self.endpoint = 'http://localhost'
        self.sniffer = Sniffer(self.endpoint)

        self.source_ip = '147.102.239.229'
        self.destination_host = 'dionyziz.com'

    @patch('breach.sniffer.requests')
    def test_sniffer_start(self, requests):
        self.sniffer.start(self.source_ip, self.destination_host)
        self.assertTrue(requests.post.called)

    @patch('breach.sniffer.requests')
    def test_sniffer_read(self, requests):
        self.sniffer.read(self.source_ip, self.destination_host)
        self.assertTrue(requests.get.called)

    @patch('breach.sniffer.requests')
    def test_sniffer_delete(self, requests):
        self.sniffer.delete(self.source_ip, self.destination_host)
        self.assertTrue(requests.post.called)
