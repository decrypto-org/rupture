const io = require('socket.io');

console.log('Rupture real-time service starting');
console.log('Listening on port ' + PORT);

const PORT = 3031;

var socket = io.listen(PORT);

socket.on('connection', function(client) {
    console.log('New connection from client ' + client.id);

    client.on('get-work', function() {
        console.log('get-work from client ' + client.id);
        client.emit('do-work', {
            url: 'http://facebook.com/?breach-test',
            amount: 3,
            timeout: 0
        });
    });
    client.on('disconnect', function() {
        console.log('Client ' + client.id + ' disconnected');
    });
});
