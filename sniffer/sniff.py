import logging
from time import sleep
from sniffer import Sniffer
from flask import Flask, request, jsonify

app = Flask(__name__)

sniffers = {}

level = logging.DEBUG
logger = logging.getLogger('sniffer')
logger.setLevel(level)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


@app.route('/start', methods=['POST'])
def start():
    '''
    Take the victim's IP, the hostname of the endpoint that is being
    attacked, the device interface and the source port of the endpoint
    and set a sniffer on all TLS connections between them.

    Arguments:
    source_ip -- the local network IP of the victim, e.g. 192.168.1.66
    destination_host -- the hostname of the attacked endpoint, e.g. dimkarakostas.com
    interface -- the device interface to use sniff on, e.g. wlan0
    destination_port -- the port of the endpoint e.g. 443

    Status code for the request:
            409: a sniffer on the same source_ip and destination host already exists
            400: parameters were not properly set
            201: a new sniffer for those arguments has been created
    '''
    data = request.get_json()
    source_ip = data['source_ip']
    destination_host = data['destination_host']
    interface = data['interface']
    destination_port = data['destination_port']

    # Check if a same sniffer already exists
    if (source_ip, destination_host) in sniffers:
        err = '409 - Sniffer (source_ip: {}, destination_host: {}) already exists.'.format(source_ip, destination_host)
        logger.warning(err)
        return str(err), 409

    params = {'source_ip': source_ip,
              'destination_host': destination_host,
              'interface': interface,
              'destination_port': destination_port}

    # Check if parameters are invalid
    try:
        sniffer = Sniffer(params)
    except AssertionError, err:
        logger.warning(err)
        return str(err), 400

    sniffers[(source_ip, destination_host)] = sniffer

    # Start the new sniffer thread and block until it has come to life
    sniffer.start()
    while not sniffer.is_alive():
        sleep(0.01)
    msg = 'Sniffer (source_ip: {}, destination_host: {}) is alive.'.format(source_ip, destination_host)
    logger.debug(msg)

    return msg, 201


@app.route('/read', methods=['GET'])
def read():
    '''
    Get the captured packets of a specific sniffer.

    Arguments:
    source_ip -- the local network IP of the victim, e.g. 192.168.1.66
    destination_host -- the hostname of the attacked endpoint, e.g. dimkarakostas.com

    Status code for the request:
            404: no sniffer exists with the given parameters
            422: sniffed packets were not formed properly
            200: sniffer exists and has made a capture
    '''
    source_ip = request.args.get('source_ip')
    destination_host = request.args.get('destination_host')

    # Get the sniffer, if exists, else return status 404
    try:
        sniffer = sniffers[(source_ip, destination_host)]
    except KeyError:
        msg = '(get_sniff) 404 Not Found: Sniffer (source_ip : {}, destination_host: {})'.format(source_ip, destination_host)
        logger.warning(msg)
        return msg, 404

    # Use the sniffer's get_capture() method to get the captured packets
    try:
        capture = sniffer.get_capture()
    except AssertionError, err:
        logger.warning(err)
        return str(err), 422

    assert('capture' in capture)

    logger.debug('Got capture with length: {}'.format(len(capture['capture'])))

    return jsonify(**capture), 200


@app.route('/delete', methods=['POST'])
def delete():
    '''
    Stop a sniffer from capturing, wait for the thread to finish and delete the sniffer.

    Arguments:
    source_ip -- the local network IP of the victim, e.g. 192.168.1.66
    destination_host -- the hostname of the attacked endpoint, e.g. dimkarakostas.com

    Status code for the request:
            404: no sniffer exists with the given parameters
            200: sniffer was deleted successfully
    '''
    data = request.get_json()
    source_ip = data['source_ip']
    destination_host = data['destination_host']

    logger.debug('Deleting sniffer (source_ip : {}, destination_host: {})...'.format(source_ip, destination_host))

    # Get the sniffer object and its source_ip and destination_host, if exists
    try:
        sniffer = sniffers[(source_ip, destination_host)]
    except KeyError:
        msg = '(get_sniff) 404 Not found: Sniffer (source_ip : {}, destination_host: {})'.format(source_ip, destination_host)
        logger.warning(msg)
        return msg, 404

    # Stop the sniffer capture and wait for the thread to join
    sniffer.stop()
    sniffer.join()

    # Delete the sniffer entries from both dictionaries
    del sniffers[(source_ip, destination_host)]

    msg = '(get_sniff) Sniffer (source_ip : {}, destination_host: {}) was deleted.'.format(source_ip, destination_host)
    logger.debug(msg)

    return msg, 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=True)
