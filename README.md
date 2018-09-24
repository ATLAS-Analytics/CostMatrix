# CostMatrix
Network cost information - measurements, collection, REST API

## Test

* adding new measurements
'''
curl -XPOST "localhost:80?source=MWT2&destination=AGLT2&rate=1.234&time=12345678.234"
'''
* retrieving measurements for one source, destination, or link
'''
curl -XGET "localhost:80?source=MWT2"
curl -XGET "localhost:80?destination=MWT2"
curl -XGET "localhost:80?source=MWT2&destination=AGLT2&"
'''
* retrieving last measurement for one link
'''
curl -XGET "localhost:80/last?source=MWT2&destination=AGLT2&"
'''

## To do

* describe REST API
* when returning results remove extraneous fields eg. _score
* add route for averaged results (ARIMA).
