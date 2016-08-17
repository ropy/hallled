var path = require('path');
var webpack = require('webpack');

var PROD = JSON.parse(process.env.PROD_ENV || '0');

module.exports = {
    entry: './index.js',
    output: {
        path: __dirname,
        filename: PROD ? 'bundle.min.js' : 'bundle.js',
        publicPath: "/build/"
    },

    module: {
        loaders: [
            {
                test: /.jsx?$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ['es2015', 'react'],
                    plugins: ['transform-es2015-arrow-functions']
                }
            }
        ]
    },
    plugins: PROD ? [
        new webpack.optimize.UglifyJsPlugin({
            compress: { warnings: false }
        })
    ] : []
};