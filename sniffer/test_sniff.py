from tl.testing.thread import ThreadAwareTestCase
import unittest
import json
from urllib import urlencode
from time import sleep

import sniff


class SniffTestCase(ThreadAwareTestCase):
    def setUp(self):
        sniff.app.config['TESTING'] = True
        self.app = sniff.app.test_client()

        self.source_ip = '192.168.1.118'
        self.destination_host = 'di.uoa.gr'
        self.destination_port = '443'
        self.interface = 'wlan0'
      
        self.data = dict(
            source_ip=self.source_ip,
            destination_host=self.destination_host,
            destination_port=self.destination_port,
            interface=self.interface
        )

        self.json_data = json.dumps(self.data)

    def _request(self, url):
        return self.app.post(
            url,
            data=self.json_data,
            content_type='application/json'
        )

    def _start(self):
        return self._request('/start')

    def _delete(self):
        return self._request('/delete')

    def _read(self):
        return self.app.get(
            '/read?' + urlencode(self.data)
        )

    def test_start_201(self):
        rv = self._start()
        self.assertEqual(rv.status_code, 201)

    def test_start_409(self):
        self._start()
        rv = self._start()
        self.assertEqual(rv.status_code, 409)

    def test_read_200(self):
        self._start()
        rv = self._read()
        self.assertEqual(rv.status_code, 200)

    def test_read_404(self):
        rv = self._read()
        self.assertEqual(rv.status_code, 404)

    def test_delete_404(self):
        rv = self._delete()
        self.assertEqual(rv.status_code, 404)

    def tearDown(self):
        sleep(0.1)
        self._delete()
        sleep(0.1)


if __name__ == '__main__':
    unittest.main()
