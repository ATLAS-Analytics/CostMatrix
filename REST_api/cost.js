// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

var elasticsearch = require('elasticsearch');
const express = require('express');

console.log('CostMatrix RESTful API server starting on: ' + PORT);

var client = new elasticsearch.Client({
    host: 'atlas-kibana.mwt2.org:9200',
    log: 'trace'
});

client.ping({
    requestTimeout: 30000,
}, function (error) {
    if (error) {
        console.error('elasticsearch cluster is down!');
    } else {
        console.log('All is well');
    }
});




function indexLinkRate(source, destination, rate) {
    client.index({
        index: 'cost_matrix',
        type: 'docs',
        id: source + destination,
        body: {
            "source": source,
            "destination": destination,
            "rate": rate
        }
    }, function (err, resp, status) {
        console.log(resp);
    });
}

// App
const app = express();

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
        res.json(resp.hits.hits);
    }, function (err) {
        console.trace(err.message);
    });



});

app.post('/', (req, res) => {
    console.log('Got POST request');
    console.log(req.query);

    if (req.query == 'undefined' || req.query == null) {
        res.send('nothing POSTed.')
        return
    }

    if (
        typeof req.query.source !== 'undefined' && req.query.source &&
        typeof req.query.destination !== 'undefined' && req.query.destination &&
        typeof req.query.rate !== 'undefined' && req.query.rate) {
        res.send(indexLinkRate(req.query.source, req.query.destination, req.query.rate));
    }
    // res.send('POST response\n');
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

