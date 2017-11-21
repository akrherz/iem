"""
 Application to save SNET data flow to the IEM Access database!
"""
from __future__ import print_function
from nwnserver import hubclient
from twisted.internet import reactor
from twisted.application import service, internet
from twisted.enterprise import adbapi
from twisted.internet.task import LoopingCall
from twisted.python import log
import re
import datetime
import sys
import os
sys.path.insert(0, os.getcwd())
import secret
import pyiem.nwnformat as nwnformat
from pyiem.observation import Observation
from pyiem.network import Table as NetworkTable
NT = NetworkTable(("KCCI", "KIMT", "KELO"))

DBPOOL = adbapi.ConnectionPool("psycopg2", database='iem', host=secret.dbhost,
                               cp_reconnect=True)
DB = {}


class NWNClientFactory(hubclient.HubClientProtocolBaseFactory):
    """
    Simple client to NWN server
    """
    maxDelay = 60.0
    factor = 1.0
    initialDelay = 60.0

    def processData(self, data):
        """
        implemented callback
        """
        reactor.callLater(0, ingest_data, data)


def find_nwsli(sid):
    """
    Figure out the NWSLI given the sid
    """
    for station in NT.sts:
        if NT.sts[station]['nwn_id'] == sid:
            return station
    return None


def ingest_data(data):
    """
    I actually ingest the data
    """
    if data is None or data == "":
        return

    tokens = re.split("\s+", data)
    if len(tokens) != 14:
        return

    siteID = tokens[1]
    if siteID not in DB:
        DB[siteID] = nwnformat.nwnformat()
        DB[siteID].sid = int(siteID)
        DB[siteID].nwsli = find_nwsli(int(siteID))
        DB[siteID].network = NT.sts.get(DB[siteID].nwsli,
                                        {'network': None})['network']
        DB[siteID].updated = False

    DB[siteID].parseLineRT(tokens)
    DB[siteID].updated = True


def saver():
    """Looping call"""
    df = DBPOOL.runInteraction(saveData)
    df.addErrback(log.err)


def saveData(txn):
    """
    Save data to the IEM database
    """
    timer_start = datetime.datetime.now()
    updates = 0
    skips = 0
    # need to call keys() as DB is voliatle
    for key in DB.keys():
        val = DB[key]
        if not val.updated or val.nwsli is None:
            skips += 1
            continue
        val.sanityCheck()
        iem = Observation(val.nwsli, val.network, val.ts)
        val.avgWinds()
        if val.tmpf is None or val.tmpf == 460:
            iem.data['tmpf'] = None
            iem.data['relh'] = None
            iem.data['dwpf'] = None
        else:
            iem.data['tmpf'] = val.tmpf
            iem.data['relh'] = val.humid
            iem.data['dwpf'] = val.dwpf

        iem.data['drct'] = val.avg_drct
        iem.data['sknt'] = val.avg_sknt
        iem.data['srad'] = val.rad
        iem.data['max_srad'] = val.xsrad
        iem.data['pres'] = val.pres
        iem.data['pday'] = float(val.pDay)
        iem.data['pmonth'] = float(val.pMonth)
        iem.data['gust'] = float(val.xsped) * 0.86897
        iem.data['max_drct'] = val.xdrct
        iem.save(txn)
        val.updated = False
        updates += 1
        val.xsped = 0
        del iem

    timer_end = datetime.datetime.now()
    print(("Time: %.2fs Updates: %s Skips: %s"
           ) % ((timer_end - timer_start).total_seconds(),
                updates, skips))

application = service.Application("NWN 2 DB")
serviceCollection = service.IServiceCollection(application)

remoteServerUser = secret.cfg['hubuser']
remoteServerPass = secret.cfg['hubpass']
clientFactory = NWNClientFactory(remoteServerUser,
                                 remoteServerPass)

client = internet.TCPClient(secret.cfg['hubserver'],
                            secret.cfg['hubport'], clientFactory)
client.setServiceParent(serviceCollection)
LC = LoopingCall(saver)
LC.start(59)
