const path = require('path')
const webpack = require('webpack')
var WebpackGitHash = require('webpack-git-hash');
var fs = require('fs')
var pkg = require('./package.json')
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
// Import config file
let isAWS = process.env.NODE_TYPE == "aws"
let _config = null
if(isAWS) {
    _config = require('./apache/config.json');
} else {
    _config = require('./config.json');
}
console.log(_config)

let config = {
    entry: './src/main.jsx',
    devServer: {
      host: '0.0.0.0',
      port: 55850,
      disableHostCheck: true
    },
    output: {
        path: path.resolve('assets'),
        // filename: 'main.js',
        publicPath: '/assets/', // './assets/'
        filename: pkg.name +'-'+ pkg.version +'.[githash].js',
        chunkFilename: pkg.name +'-chunk.[githash].js'
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    module: {
        loaders: [
        {
            test: /\.(js|jsx)$/,
            loader: ['react-hot-loader/webpack', 'babel-loader'],
            exclude: /node_modules/
        },
        {
            test: /\.css$/,
            loader: "style-loader!css-loader"
        },
        {
            test: /\.(png|woff|woff2|eot|ttf|svg)$/,
            loader: 'url-loader?limit=100000'
        }]
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(process.env.NODE_ENV),
                NODE_TYPE: JSON.stringify(process.env.NODE_TYPE)
            }
        }),
        new webpack.DefinePlugin({
            DEBUG: _config.debug,
            REVERSEPROXYON: _config.reverseProxyOn
        }),
        new webpack.DefinePlugin({
            BITLY: JSON.stringify({
                baseURL: "http://scope.aertslab.org",
                token: "8422dd882b60604d327939997448dd1b5c61f54e"
            }),
            BACKEND: JSON.stringify({
                httpProtocol: _config.httpProtocol,
                wsProtocol: _config.wsProtocol,
                host: "127.0.0.1",
                WSport: _config.xPort,
                XHRport: _config.pPort,
                RPCport: _config.gPort
            }),
            FRONTEND: JSON.stringify({
                httpProtocol: _config.httpProtocol,
                wsProtocol: _config.wsProtocol,
                host: _config.domainName
            })
        }),
        new WebpackGitHash({
            cleanup: true,
            callback: function(versionHash) {
                var indexHtml = fs.readFileSync('./index.html', 'utf8');
                indexHtml = indexHtml.replace(/src="\.\/assets\/.*\.js"/, 'src="./assets/'+ pkg.name +'-'+ pkg.version +'.' + versionHash + '.js"');
                fs.writeFileSync('./index.html', indexHtml);
            }
        })

    ]
}

if (process.env.NODE_ENV === 'production') {
    if(process.env.NODE_TYPE !== 'aws') { // Take huge time on free tier aws
        config.plugins.push(
            new UglifyJsPlugin({
                parallel: true,
                uglifyOptions: {
                    warnings: false,
                }
            })
        )
    }
    config.plugins.push(
        new webpack.optimize.OccurrenceOrderPlugin()
    )
} else {
    config.plugins.push(new webpack.NamedModulesPlugin())
    config.entry = ['react-hot-loader/patch', config.entry]
}

// config.node = { fs: 'empty', child_process: 'empty' };

module.exports = config
