import netifaces
import ipaddress
import subprocess
import os
from bs4 import BeautifulSoup


def get_interface():
    return netifaces.gateways()['default'][netifaces.AF_INET][1]


def get_local_IP():
    def_gw_device = get_interface()
    return netifaces.ifaddresses(def_gw_device)[netifaces.AF_INET][0]['addr']


def get_netmask():
    def_gw_device = get_interface()
    return netifaces.ifaddresses(def_gw_device)[netifaces.AF_INET][0]['netmask']


def scan_network():
    possible_victims = []

    local_ip = get_local_IP()
    netmask = get_netmask()
    network = str(ipaddress.IPv4Network((local_ip.decode('utf-8'), netmask.decode('utf-8')), strict=False))

    proc = subprocess.Popen(['sudo', 'nmap', '-oX', '-', '-sP', network], stdout=subprocess.PIPE, preexec_fn=os.setpgrp)
    nmap_output = proc.communicate()[0]
    soup = BeautifulSoup(nmap_output)
    for address in soup.findAll('address'):
        addr_attrs = dict(address.attrs)
        if addr_attrs[u'addrtype'] == 'ipv4':
            possible_victims.append(addr_attrs[u'addr'])
    return possible_victims


if __name__ == '__main__':
    print scan_network()
