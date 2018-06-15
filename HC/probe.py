#!/usr/bin/env python
import requests
import time
import json as simplejson

ts = int(round(time.time() * 1000))

server = 'http://costmatrix.slateci.net:80/'

print('--------------------------------- Uploading result ---------------------------------')
data = dict(source="SITE_FROM", destination="SITE_TO", rate=123.456, time=ts)
u = requests.post(server, params=data)
print(u.text)

event = {}
event['source'] = "SITE_FROM"
event['destination'] = "SITE_TO"
event['log'] = 'asdfasdf sdfasdf  asdfd'
event['time'] = ts
u = requests.post(server + 'error/', params=event)
# req.add_header('Content-Type', 'application/json')
print(u.text)
