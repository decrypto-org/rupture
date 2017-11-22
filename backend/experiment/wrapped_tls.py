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


def get_response(url):
    parsed = urlparse(url)
    h = ManagedHTTPTLSConnection(parsed.netloc, 443)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
    }
    h.request("GET", parsed.path + '?' + parsed.query, '', headers)
    h.getresponse()


if __name__ == '__main__':
    url = str(u'https://ruptureit.com/test.php?reflection=^c^b^e^d^g^f^i^h^k^j^m^l^o^n^q^p^s^r^u^t^w^v^y^x^z^impera^K^')
    print get_response(url)
