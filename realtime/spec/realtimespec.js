const spawn = require('child_process').spawn;
const client = require('socket.io-client');
const express = require('express');
const bodyParser = require('body-parser');

function runServer() {
    server = spawn(
        'node',
        [
            '--harmony',
            'index.js',
            '--port', '9909',
            '--backend-host', 'localhost',
            '--backend-port', '9908'
        ]
    );

    server.stdout.on('data', (data) => {
        console.log(data.toString());
    });
    server.stderr.on('data', (data) => {
        console.log(data.toString());
    });
    server.on('exit', () => {
        console.log('Server terminated');
    });

    return server;
}

function connect() {
    const socket = client('http://localhost:9909');

    socket.on('error', () => {});

    return socket;
}

describe('real-time service', () => {
    let server,
        socket,
        socket2;

    beforeEach(() => {
        server = runServer();
        socket = connect();
    });

    it('listens for websocket connections', (done) => {
        socket.on('connect', done);
    });

    it('exchanges hello messages', function(done) {
        socket.on('connect', () => {
            socket.emit('client-hello', {victim_id: 5});
            socket.on('server-hello', done);
        });
    });

    it('does not duplicate clients running', (done) => {
        socket.on('connect', () => {
            socket.emit('client-hello', {victim_id: 5});
        });
        socket.on('server-hello', () => {
            socket2 = connect();
            socket2.on('connect', () => {
                socket2.emit('client-hello', {victim_id: 5});
            });
            socket2.on('server-nowork', () => {
                socket2.close();
                done();
            });
        });
    });

    describe('backend communication', () => {
        let fakeServer;

        function fakeBackend(listenCallback, method, url, getCallback) {
            const app = express();
            app.use(bodyParser.json());
            app[method](url, getCallback);
            fakeServer = app.listen(9908, listenCallback);
        }

        beforeEach((done) => {
            socket.on('connect', () => {
                socket.emit('client-hello', {victim_id: 5});
                done();
            });
        });

        it('requests work from the backend', function(done) {
            fakeBackend(
                () => {
                    socket.emit('get-work');
                },
                'get',
                '/breach/get_work/5',
                done
            );
        });

        it('reports work-completed to the backend', function(done) {
            fakeBackend(
                () => {
                    socket.emit('work-completed', {work: {}, success: true});
                },
                'post',
                '/breach/work_completed/5',
                (request, response) => {
                    expect(request.body.success).toBe(true);
                    done();
                }
            );
        });

        it('reports failed work-completed after a client disconnects', function(done) {
            fakeBackend(
                () => {
                    socket.close();
                },
                'post',
                '/breach/work_completed/5',
                (request, response) => {
                    expect(request.body.success).toBe(false);
                    done();
                }
            );
        });

        afterEach(() => {
            fakeServer.close();
        });
    });

    afterEach(() => {
        server.kill();
        socket.close();
    });
});
