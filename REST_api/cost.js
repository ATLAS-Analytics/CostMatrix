// Constants
const PORT = 80;
const HOST = '0.0.0.0';

var elasticsearch = require('elasticsearch');
const express = require('express');

console.log('CostMatrix RESTful API server starting on: ' + PORT);

var client = new elasticsearch.Client({
    host: 'atlas-kibana.mwt2.org:9200'
    // log: 'error' // trace, warning
});

function test_ES_connection() {
    client.ping({
        requestTimeout: 30000,
    }).then(all_is_well, all_is_not_well);
}

function all_is_well(err, resp, stat) {
    console.log('All is well');
}

function all_is_not_well(err, resp, stat) {
    console.error('elasticsearch cluster is down!');
    process.exit(1);
}


// App
const app = express();

app.get('/last', (req, res) => {
    console.log('Got GET last request!');
    console.log(req.query);

    source = '*';
    destination = '*';

    if (typeof req.query.source !== 'undefined' && req.query.source) {
        source = req.query.source;
    }
    if (typeof req.query.destination !== 'undefined' && req.query.destination) {
        destination = req.query.destination;
    }

    client.search({
        index: 'cost_matrix',
        type: 'docs',
        body: {
            size: 9999,
            query: {
                bool: {
                    must: {
                        term: { "last": true }
                    },
                    should: [
                        { wildcard: { "source": source } },
                        { wildcard: { "destination": destination } }
                    ]
                }
            }
        }
    }).then(function (resp) {
        console.log(resp.hits.hits);
        res.json(200, resp.hits.hits);
    }, function (err) {
        console.trace(400, err.message);
        res.status(500).send('could not get data. Error: ' + err.message)
    });



});

app.get('/', (req, res) => {
    console.log('Got GET request!');
    console.log(req.query);

    source = '*';
    destination = '*';

    if (typeof req.query.source !== 'undefined' && req.query.source) {
        source = req.query.source;
    }
    if (typeof req.query.destination !== 'undefined' && req.query.destination) {
        destination = req.query.destination;
    }

    client.search({
        index: 'cost_matrix',
        type: 'docs',
        body: {
            size: 9999,
            query: {
                bool: {
                    should: [
                        { wildcard: { "source": source } },
                        { wildcard: { "destination": destination } }
                    ]
                }
            }
        }
    }).then(function (resp) {
        console.log(resp.hits.hits);
        res.json(200, resp.hits.hits);
    }, function (err) {
        console.trace(400, err.message);
        res.status(500).send('could not get data. Error: ' + err.message)
    });



});

app.post('/', (req, res) => {
    // console.log('Got POST request');
    // console.log(req.query);

    if (req.query == 'undefined' || req.query == null) {
        res.status(400).send('nothing POSTed.')
        return
    }

    if (
        typeof req.query.source !== 'undefined' && req.query.source &&
        typeof req.query.destination !== 'undefined' && req.query.destination &&
        typeof req.query.rate !== 'undefined' && req.query.rate &&
        typeof req.query.time !== 'undefined' && req.query.time
    ) {
        client.index({
            requestTimeout: 10000,
            index: 'cost_matrix',
            type: 'docs',
            id: req.query.source + '_' + req.query.destination,
            body: {
                "source": req.query.source,
                "destination": req.query.destination,
                "rate": req.query.rate,
                "timestamp": parseFloat(req.query.time),
                "last": true
            }
        }).then(function (resp) {
            // console.log("OK 1");
        }, function (err) {
            console.log(err.message);
            console.log(req.query);
        });

        client.index({
            requestTimeout: 10000,
            index: 'cost_matrix',
            type: 'docs',
            id: req.query.source + '_' + req.query.destination + '_' + req.query.time,
            body: {
                "source": req.query.source,
                "destination": req.query.destination,
                "rate": req.query.rate,
                "timestamp": parseFloat(req.query.time)
            }
        }).then(function (resp) {
            // console.log("OK 2");
            res.status(200).send('Data indexed')
        }, function (err) {
            console.log(err.message);
            console.log(req.query);
            res.status(500).send('could not index  data. Error: ' + err.message)
        });

    } else {
        res.status(400).send('requires source, destination, rate and time.')
    }
});

app.post('/error', (req, res) => {
    // console.log('Got POST error request');
    // console.log(req.query);

    if (req.query == 'undefined' || req.query == null) {
        res.status(400).send('nothing POSTed.')
        return
    }

    if (
        typeof req.query.source !== 'undefined' && req.query.source &&
        typeof req.query.destination !== 'undefined' && req.query.destination &&
        typeof req.query.log !== 'undefined' && req.query.log &&
        typeof req.query.time !== 'undefined' && req.query.time
    ) {
        client.index({
            requestTimeout: 10000,
            index: 'cost_matrix',
            type: 'docs',
            id: req.query.source + '_' + req.query.destination,
            body: {
                "source": req.query.source,
                "destination": req.query.destination,
                "log": req.query.log,
                "timestamp": parseFloat(req.query.time),
                "last": true
            }
        }).then(function (resp) {
            // console.log("OK 1");
        }, function (err) {
            console.log(err.message);
        });

        client.index({
            requestTimeout: 10000,
            index: 'cost_matrix',
            type: 'docs',
            id: req.query.source + '_' + req.query.destination + '_' + req.query.time,
            body: {
                "source": req.query.source,
                "destination": req.query.destination,
                "log": req.query.log,
                "timestamp": parseFloat(req.query.time)
            }
        }).then(function (resp) {
            // console.log("OK 2");
            res.status(200).send('Log Data indexed')
        }, function (err) {
            console.log(err.message);
            console.log(req.query);
            res.status(500).send('could not fully index log data. Error: ' + err.message)
        });

    } else {
        res.status(400).send('requires source, destination, log and time.')
    }
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

