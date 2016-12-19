import netifaces


def get_interface():
    return netifaces.gateways()['default'][netifaces.AF_INET][1]


def get_local_IP():
    def_gw_device = get_interface()
    return netifaces.ifaddresses(def_gw_device)[netifaces.AF_INET][0]['addr']
