import netifaces


def get_interface():
    return netifaces.gateways()['default'][netifaces.AF_INET][1]
