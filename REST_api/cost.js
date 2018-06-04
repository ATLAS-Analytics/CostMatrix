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


// App
const app = express();
app.get('/', (req, res) => {
    res.send('Hello world\n');
});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

// client.search({
//     index: 'twitter',
//     type: 'tweets',
//     body: {
//         query: {
//             match: {
//                 body: 'elasticsearch'
//             }
//         }
//     }
// }).then(function (resp) {
//     var hits = resp.hits.hits;
// }, function (err) {
//     console.trace(err.message);
// });