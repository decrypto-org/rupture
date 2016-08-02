var path = require('path');
var webpack = require('webpack');

module.exports = {
    entry: {
        main: ['./main.js']
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].js'
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['es2015'],
                    cacheDirectory: true
                }
            }
        ]
    },
    stats: {
        colors: true
    },
    devtool: 'source-map'
};
