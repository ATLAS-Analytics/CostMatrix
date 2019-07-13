#!/usr/bin/env python
import sys
import os
import time
from datetime import datetime
import tools

if os.environ.get("RUCIO_ACCOUNT") != None:
    rucio_account = os.environ.get("RUCIO_ACCOUNT")
else:
    print("no RUCIO_ACCOUNT environment found. Please set it before using this program.")
    sys.exit(1)

endpoints = tools.getXROOTendpoints()
ddms = tools.getDDMendpoints()

reps = tools.find_replicas('mc15_13TeV', 'HITS.06828093._000096.pool.root.1')

docs = []
for ep in endpoints:
    print('------------------------------------------------------------')
    site = ep['site']
    doc = {'_index': 'testing_xrootd', '_type': 'docs', 'site': site, 'issues': [], 'endpoint': ep['name']}

    print('Site:', site, 'doortype:', ep['door_type'], 'address:', ep['address'])

    if ep['state'] != 'ACTIVE':
        doc['issues'].append('xrootd door not active')
    if ep['door_type'] == '':
        doc['issues'].append('door type not set')
    if ep['door_type'] == 'internal' or ep['door_type'] == 'proxyinternal':
        doc['issues'].append("can't test this door")

    sites_ddms = ddms[site]
    # print(sites_ddms)

    found = False
    for ddm in sites_ddms:
        if ddm in reps:
            fp = reps[ddm]
            if not fp.startswith(ep['address']):
                doc['issues'].append('rucio returns different door: ' + fp)
                break
                #fp = ep['address'] + fp[fp.rfind('//'):]
            print('to check: ', fp)
            doc['path'] = fp
            found = True
            break
    if not found:
        doc['issues'].append("no replica at the site")

    if len(doc['issues']):
        print(doc['issues'])

    docs.append(doc)

for d in docs:
    print(d)
print('Done.')


print('creating script to execute')

ts = datetime.utcnow().strftime("%Y%m%dT%H0000Z")
logpostfix = '_' + ts + '.log'
redstring = ' - 2>&1 >/dev/null | cat >'

try:
    with open('checkDirect.sh', 'w') as f:
        for d in docs:
            d['timestamp'] = ts
            if 'path' not in d:
                continue
            logfile = d['endpoint'] + logpostfix
            cpcomm = 'timeout 270 xrdcp -d 2 -f -np '
            comm = cpcomm + d['path'] + redstring + logfile + ' & \n'
            f.write('echo "command executed:\n ' + comm + '" >> ' + logfile + '\n')
            f.write('echo "========================================================================" >> ' + logfile + '\n')
            f.write(comm)
        f.close()
except:
    print("Unexpected error:", sys.exc_info()[0])
# sys.exit(0)
print('executing all of the xrdcps in parallel. 5 min timeout.')
com = tools.Command("source ./checkDirect.sh")
com.run(300)
time.sleep(250)


print('checking log files')

# checking which sites gave their own file directly
for d in docs:  # this is file to be asked for
    if 'path' not in d:
        continue
    logfile = d['endpoint'] + logpostfix
    try:
        with open(logfile, 'r') as f:
            lines = f.readlines()
            succ = False
            for l in lines:
                # print l
                if tools.isMsgOK(l):
                    succ = True
                    break
            if succ == True:
                print(logfile, "works")
                d['state'] = "Works"
            else:
                print(logfile, "problem")
                d['state'] = "problem"
    except:
        print "Unexpected error:", sys.exc_info()[0]


tools.storeInES(docs)

print('All done.')
