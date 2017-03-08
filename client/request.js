const Request = {
    _img: null,
    make(url, callback) {
        console.log('Making request to ' + url);

        this._img = new Image();
        this._img.onerror = callback;
        this._img.src = url;
    },
    cancel() {
        this._img.src = '';
    }
};

const Collection = {
    _ONE_REQUEST_DEFAULT_TIMEOUT: 5000,
    _SENTINEL: '^',
    create(url, {amount, alignmentalphabet, oneRequestTimeout}, onOneSuccess, onAllSuccess, onError) {
        const requests = [];
        let loadingTimeout,
            loadedCount = 0;

        if (oneRequestTimeout === 0) {
            throw 'oneRequestTimeout should not be zero';
        }

        oneRequestTimeout = oneRequestTimeout || this._ONE_REQUEST_DEFAULT_TIMEOUT;

        console.log('Creating request collection of ' + amount + ' requests to URL: ' + url);
        console.log('Using one request time out value of ' + oneRequestTimeout);

        const resetTimeout = () => {
            clearTimeout(loadingTimeout);
            loadingTimeout = setTimeout(() => {
                for (let i = 0; i < amount; ++i) {
                    requests[i].cancel();
                }
                clearTimeout(loadingTimeout);
                onError();
            }, oneRequestTimeout);
        };
        const allCompleted = () => {
            clearTimeout(loadingTimeout);
            onAllSuccess();
        };
        const oneLoaded = (index) => {
            console.log();

            resetTimeout();
            console.log('Completed request: ' + index);
            ++loadedCount;

            onOneSuccess(index);

            if (loadedCount == amount) {
                allCompleted();
            }
        };

        let antiBrowserCaching = Math.random() * Number.MAX_SAFE_INTEGER;

        for (let i = 0; i < amount; ++i) {
            let alignmentPadding = alignmentalphabet.substr(0, i % alignmentalphabet.length);
            let request = Request.make(url + alignmentPadding + this._SENTINEL + '&' + (antiBrowserCaching + i), oneLoaded.bind({}, i));
            requests.push(request);
        }
    }
};

module.exports = {Request, Collection};
