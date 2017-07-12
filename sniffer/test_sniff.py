from tl.testing.thread import ThreadAwareTestCase
import unittest
from mock import patch
import json
from urllib import urlencode
import app


class BaseTestCase(ThreadAwareTestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

        self.source_ip = '192.168.1.118'
        self.destination_host = 'di.uoa.gr'
        self.destination_port = '443'
        self.interface = 'wlan0'
        self.calibration_wait = 0.0

        self.data = dict(
            source_ip=self.source_ip,
            destination_host=self.destination_host,
            destination_port=self.destination_port,
            interface=self.interface,
            calibration_wait=self.calibration_wait
        )

    @patch('app.Sniffer.start', return_value=None)
    @patch('app.Sniffer.isAlive', return_value=True)
    def _request(self, url, patched_sniffer_start, patched_sniffer_isAlive):
        return self.app.post(
            url,
            data=json.dumps(self.data),
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

    def tearDown(self):
        self._delete()


class ResponseCodesTestCase(BaseTestCase):
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


class CalibrationTestCase(BaseTestCase):
    @patch('app.sleep', return_value=None)
    def test_sleep(self, patched_sniffer_sleep):
        self.data['calibration_wait'] = 1000000.0
        self._start()
        app.sleep.assert_called_with(1000000.0)


if __name__ == '__main__':
    unittest.main()
