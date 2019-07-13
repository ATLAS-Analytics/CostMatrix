import requests
import sys

try:
    import simplejson as json
except ImportError:
    import json

import subprocess
import threading

from elasticsearch import Elasticsearch, exceptions as es_exceptions
from elasticsearch import helpers

es = Elasticsearch(hosts=[{'host': 'atlas-kibana.mwt2.org', 'port': 9200}], timeout=60)

import rucio
import rucio.client
import rucio.common.config as conf

rrc = rucio.client.replicaclient.ReplicaClient()


def getXROOTendpoints():
    print('---------------getting xrootd endpoints from AGIS. ---------------')
    endpoints = []
    try:
        req = requests.get("http://atlas-agis-api.cern.ch/request/service/query/get_se_services/?json&state=ACTIVE&flavour=XROOTD", None)
        res = req.json()
        for s in res:
            #             print(s)
            print(s["name"], s["rc_site"], s["endpoint"], s['door_type'], s['state'])
            endpoints.append({'name': s["name"], 'site': s["rc_site"], 'address': s["endpoint"],
                              'door_type': s['door_type'], 'state': s['state']})
        # print res
        print('Done.')
    except:
        print("Could not get xrootd endpoints from AGIS. Exiting...")
        print("Unexpected error:%s" % str(sys.exc_info()[0]))
        sys.exit(1)
    return endpoints


def getDDMendpoints():
    print('---------------getting ddm endpoints from AGIS. ---------------')
    ddms = {}
    try:
        req = requests.get("http://atlas-agis-api.cern.ch/request/ddmendpoint/query/get_ddm_endpoint/?json", None)
        res = req.json()
        for s in res:
            #             print(s)
            print(s["name"], s["rc_site"])
            if s["rc_site"] not in ddms:
                ddms[s['rc_site']] = []
            ddms[s['rc_site']].append(s["name"])
        # print res
        print('Done.')
    except:
        print("Could not get dmm endpoints from AGIS. Exiting...")
        print("Unexpected error:%s" % str(sys.exc_info()[0]))
        sys.exit(1)
    return ddms


def storeInES(data):
    success = False
    try:
        res = helpers.bulk(es, data, raise_on_exception=True, request_timeout=60)
        print("inserted:", res[0], 'errors:', res[1])
        success = True
    except es_exceptions.ConnectionError as error:
        print('ConnectionError ', error)
    except es_exceptions.TransportError as error:
        print('TransportError ', error)
    except helpers.BulkIndexError as error:
        print(error[0])
        for i in error[1]:
            print(i)
    except:
        print('Something seriously wrong happened.')
    return success


def find_replicas(scope, name):
    try:
        reps = rrc.list_replicas([{'scope': scope, 'name': name}], schemes=['root'])
    except:
        print("Could not get replicas from rucio.")

    res = {}
    for r in reps:
        # print(r)
        for key, value in r['rses'].iteritems():
            if len(value) != 1:
                print(">>>>>>> Problem with replica <<<<<<<<", key, value)
                continue
            res[key] = value[0]
            print(key, value)

    return res


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print('command started: ', self.cmd)
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('Terminating process')
            self.process.terminate()
            thread.join()
        return self.process.returncode


def isMsgOK(l):
    if l.count('[SUCCESS]') == 0:
        return False
    if l.count('Close returned from') == 0:
        return False
    return True
