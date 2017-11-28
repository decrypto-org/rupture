import httplib
from urlparse import urlparse
from tlslite.tlsconnection import TLSConnection
from tlslite import HTTPTLSConnection
from tlslite.integration.clienthelper import ClientHelper


class DebugSocket(object):
    def __init__(self, sock):
        self.sock = sock
        self.received = ''
        self.sent = ''

    def __getattr__(self, name):
        if name in ['sendall', 'close']:
            return getattr(self.sock, name)

    def send(self, *args, **kwargs):
        data = args[0]
        self.sent += data
        return self.sock.send(*args, **kwargs)

    def recv(self, *args, **kwargs):
        data = self.sock.recv(*args, **kwargs)
        self.received += data
        return data


class ManagedHTTPTLSConnection(HTTPTLSConnection):
    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.debug_socket = DebugSocket(self.sock)
        self.sock = TLSConnection(self.debug_socket)
        self.sock.ignoreAbruptClose = self.ignoreAbruptClose
        ClientHelper._handshake(self, self.sock)

    def get_encrypted_response(self):
        return self.debug_socket.received

    def get_encrypted_request(self):
        return self.debug_socket.sent


class MockSniffer(object):
    def __init__(self, params):
        self.endpoint = params['snifferendpoint']
        self.source_ip = params['sourceip']
        self.destination_host = params['host']
        self.interface = params['interface']
        self.destination_port = params['port']
        self.calibration_wait = params['calibration_wait']

        self.samplesize = 64

    def get_sniffer_state(self):
        state = {
            'source_ip': self.source_ip,
            'destination_host': self.destination_host,
            'interface': self.interface,
            'destination_port': self.destination_port,
            'calibration_wait': self.calibration_wait
        }
        return state

    def set_samplesize(self, size):
        self.samplesize = size

    def set_data(self, data):
        self.app_data = data

    def start(self):
        self.app_data = ''

    def read(self):
        return {
            'records': self.samplesize,
            'data': self.app_data
        }

    def delete(self):
        self.app_data = ''


def parse(data):
    if not data:
        return ''

    TLS_HEADER_LENGTH = 5
    TLS_CONTENT_TYPE = 0
    TLS_LENGTH_MAJOR = 3
    TLS_LENGTH_MINOR = 4

    tls_type = ord(data[TLS_CONTENT_TYPE])
    length = 256 * ord(data[TLS_LENGTH_MAJOR]) + ord(data[TLS_LENGTH_MINOR])

    app_data = data[TLS_HEADER_LENGTH:TLS_HEADER_LENGTH + length] if tls_type == 23 else ''
    return app_data + parse(data[TLS_HEADER_LENGTH + length:])


def get_response(url, plaintext=False):
    parsed = urlparse(url)
    h = ManagedHTTPTLSConnection(parsed.netloc, 443)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
    }
    h.request("GET", parsed.path + '?' + parsed.query, '', headers)

    r = h.getresponse().read()
    if plaintext:
        return r

    return parse(h.get_encrypted_response())


if __name__ == '__main__':
    url = str(u'https://ruptureit.com/test.php?reflection=^c^b^e^d^g^f^i^h^k^j^m^l^o^n^q^p^s^r^u^t^w^v^y^x^z^impera^K^')
    print get_response(url)
