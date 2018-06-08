#!/usr/bin/env python

# it takes list of active xrootd doors from AGIS, copy a file from each of them
# uploads MiB/s results to UChicago costmatrix storage

import subprocess
import threading
import os
import sys
import random
import math
import logging
import time

import urllib
import urllib2
import json as simplejson

import requests
from rucio.client import Client

server = 'http://192.170.227.237:8080'


class Replica:
    se_mapping = None

    def __init__(self, se, address):
        self.se = se
        self.address = address
        self.site = ''
        if Replica.se_mapping == None:
            Replica.se_mapping = getSEmapping()
            print(Replica.se_mapping)
        for site in Replica.se_mapping:
            if self.se in Replica.se_mapping[site]:
                self.site = site
                break
        if self.site == '':
            print('Site Unknown!  ' + self.se)

    def prnt(self):
        print('name: ' + self.se + '\tsite:' + self.site + '\taddress:' + self.address)


class Command(object):
    def __init__(self, cmd, sn):
        self.cmd = cmd
        self.cn = sn
        tv = random.randint(0, 15 * 60)
        print(sn, "will wait", tv, "seconds to start")
        self.next = time.time() + tv
        self.process = None
        self.thread = None
        self.counter = 0

    def run(self, timeout, foreground=False):
        def target():
            print('command started', self.cn, self.counter)
            self.next = time.time() + 24 * 3600  # this prevents it from restarting in case it's still running
            self.process = subprocess.Popen(self.cmd, shell=True)
            if (foreground):
                self.process.communicate()

        self.thread = threading.Thread(target=target)
        self.thread.start()

        self.thread.join(timeout)
        if self.thread.is_alive():
            print('Terminating process')
            try:
                self.process.terminate()
                print('command killed', self.cn)
            except OSError as e:
                print >>sys.stderr, "Forced termination failed:", e
            self.thread.join()
        return  # self.process.returncode


def upload(SITE_FROMLOG, SITE_TO):
    SITE_FROM = SITE_FROMLOG.replace('.log', '')

    print('Upload:', SITE_FROM, ' -> ', SITE_TO)
    if not os.path.isfile(SITE_FROMLOG):
        print("log file for site", site, "missing")
        return

    retCode = '-1'
    rate = 0
    with open(SITE_FROMLOG, 'r') as f:
        lines = f.readlines()

        for l in lines:
            l = l.strip()

            if l.count('COPYTIME=') > 0:
                res = l.replace('COPYTIME=', '')
                if res == '':
                    rate = 0
                    continue
                if float(res) > 0:
                    rate = 90.4414399 / float(res)
                else:
                    rate = 0

            if l.count('EXITSTATUS') > 0:
                retCode = l.replace('EXITSTATUS=', '')

        if retCode == '0':
            # print '--------------------------------- Uploading result ---------------------------------'
            # print rate
            ts = int(round(time.time() * 1000))
            data = dict(source=SITE_FROM, destination=SITE_TO, rate=rate, time=ts)
            u = requests.post(server, params=data)
            print(u.text)

        else:
            print('non 0 exit code. will not upload result. ')
            data = dict(source=SITE_FROM, destination=SITE_TO, log=','.join(lines), time=ts)
            u = requests.post(server, params=data)
            print(u.text)


def get_replicas(scope='user.mlassnig', filename='user.mlassnig.pilot.test.single.hits'):

    c = Client()

    replicas = c.list_replicas(
        dids=[{'scope': scope, 'name': filename}], schemes=['root']
        # , client_location={'site': 'MWT2'}
    )
    res = []
    for replica in replicas:
        r = replica['pfns']
        for p in r:
            res.append(Replica(r[p]['rse'], p))
    return res


def getSEmapping():
    mapping = {}
    print('Geting ddm to site mapping from AGIS...')

    try:
        req = urllib2.Request("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json", None)
        opener = urllib2.build_opener()
        f = opener.open(req)
        res = simplejson.load(f)
        for s in res:
            if "ddmendpoints" not in s or s["ddmendpoints"] == None or s["ddmendpoints"] == {}:
                continue
            for si in s["ddmendpoints"]:  # this is mostly one
                if si not in mapping:
                    mapping[si] = []
                for se in s["ddmendpoints"][si]:
                    mapping[si].append(se)
    except:
        print("Unexpected error:", sys.exc_info()[0])

    return mapping


def main():

    maxParallel = 6
    currParallel = 0

    if len(sys.argv) == 3:
        # print 'uploading results from file ', sys.argv[1]
        # print 'I was told the site name is ', sys.argv[2]
        upload(sys.argv[1], sys.argv[2])
        return

    QUEUE = ''
    SITE = ''
    if os.environ.has_key('PANDA_SITE_NAME'):
        QUEUE = os.environ['PANDA_SITE_NAME']
    else:
        print('ERROR. PANDA_SITE_NAME is not defined. Exiting.')
        sys.exit(0)
    print('RUNNING in QUEUE: ', QUEUE)

    # finding which site is this
    try:
        req = urllib2.Request("http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&panda_resource=" + QUEUE, None)
        opener = urllib2.build_opener()
        f = opener.open(req)
        res = simplejson.load(f)
        if len(res) == 0:
            print('could not get site name from queue name. exiting.')
            sys.exit(0)
        SITE = res[0]["rc_site"]
        if SITE == 'GRIF':
            SITE = res[0]["atlas_site"]
        print("at SITE:", SITE)
    except:
        print("Unexpected error:", sys.exc_info()[0])

    rs = get_replicas()

    for r in rs:
        r.prnt()
        with open('exec_' + r.site + '.sh', 'w') as f:

            logfile = r.site + '.log'

            f.write("""#!/bin/bash\n""")
            f.write('echo "--------------------------------------"\n ')
            f.write('`which time`  -f "COPYTIME=%e\\nEXITSTATUS=%x" -o ' + logfile +
                    ' xrdcp -np ' + r.address + """ - > /dev/null  2>&1 \n""")
            f.write('python cost_matrix_probe.py ' + logfile + " " + SITE + "\n")
            #f.write('rm '+logfile+"\n")

        f.close()
        os.chmod('exec_' + r.site + '.sh', 0755)

    comms = []
    for r in rs:
        comm = Command("source ./exec_" + r.site + ".sh", r.site)
        comms.append(comm)

    for w in range(86100):
        time.sleep(1)
        ct = time.time()
        for c in comms:
            if c.process is not None:
                if c.process.poll() is not None:
                    c.process.wait()
                    print 'command finished', c.cn, c.counter
                    currParallel -= 1
                    c.counter += 1
                    c.process = None
                    c.next = time.time() + 15 * 60
            if ct > c.next:
                if currParallel > maxParallel:
                    print('Already having', currParallel, "streams. Delaying start of", c.cn)
                    continue
                c.run(3600)
                currParallel += 1

    print 'stopping.'


if __name__ == "__main__":
    main()
