from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/set_sniffer')
def set_sniffer():
    return 'Not implemented', 200


@app.route('/get_capture')
def get_capture():
    return 'Not implemented', 200


@app.route('/delete_sniffer')
def delete_sniffer():
    return 'Not implemented', 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9000, debug=True)
