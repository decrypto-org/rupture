const {Request, Collection} = require('../request.js');
require('jasmine-expect');

describe('request', () => {
    var requestsMade = [],
        originalImage;

    function createMockImage(requestsMade) {
        return function() {
            Object.defineProperties(this, {
                'src': {
                    'set': (value) => {
                        requestsMade.push(value);
                        this.onerror();
                    }
                }
            });
        };
    }

    global.Image = createMockImage(requestsMade);

    beforeEach(() => {
        originalImage = global.Image;
        requestsMade = [];
    });

    afterEach(() => {
        global.Image = originalImage;
    });

    it('uses an image to perform a cross-origin request', (done) => {
        Request.make('https://www.ruptureit.com/', done);
        expect(requestsMade).toContain('https://www.ruptureit.com/');
    });
});

describe('collection', () => {
    it('makes multiple requests', () => {
        const callbacks = [],
              urls = [];

        spyOn(Request, 'make').and.callFake((url, callback) => {
            urls.push(url);
            callbacks.push(callback);
        });

        const onOneSuccess = jasmine.createSpy(),
              onAllSuccess = jasmine.createSpy(),
              onError = jasmine.createSpy();

        Collection.create('https://ruptureit.com/reflect?q=reflection', {
            amount: 3,
            alignmentalphabet: 'abc'
        }, onOneSuccess, onAllSuccess, onError);

        expect(Request.make.calls.count()).toBe(3);
        expect(onOneSuccess).not.toHaveBeenCalled();
        expect(onAllSuccess).not.toHaveBeenCalled();
        expect(onError).not.toHaveBeenCalled();

        callbacks[0]();

        expect(onOneSuccess).toHaveBeenCalled();
        expect(onAllSuccess).not.toHaveBeenCalled();
        expect(onError).not.toHaveBeenCalled();

        callbacks[1]();
        callbacks[2]();

        expect(onOneSuccess.calls.count()).toBe(3);
        expect(onAllSuccess).toHaveBeenCalled();
        expect(onError).not.toHaveBeenCalled();

        expect(urls[0]).toStartWith('https://ruptureit.com');

        // anti-caching
        ending0 = urls[0].split('&')[1];
        ending1 = urls[1].split('&')[1];

        expect(ending0).not.toBe(ending1);
    });
});
