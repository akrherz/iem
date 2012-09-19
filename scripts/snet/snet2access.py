"""
 Application to save SNET data flow to the IEM Access database!
"""

from nwnserver import hubclient
from twisted.internet import reactor
from twisted.application import service, internet
from twisted.enterprise import adbapi
from twisted.internet.task import LoopingCall
import traceback
import secret
import re
import mx.DateTime
import nwnformat
import access
import network
NT = network.Table(("KCCI", "KIMT", "KELO"))

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
                   

def find_nwsli( sid ):
    """
    Figure out the NWSLI given the sid
    """
    for station in NT.sts.keys():
        if int(NT.sts[station]['nwn_id']) == sid:
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
    if not DB.has_key(siteID):
        DB[siteID] = nwnformat.nwnformat()
        DB[siteID].sid = int(siteID)
        DB[siteID].nwsli = find_nwsli( int(siteID) )
        DB[siteID].network = NT.sts.get(DB[siteID].nwsli, 
                                        {'network': None})['network']
        DB[siteID].updated = False

    DB[siteID].parseLineRT(tokens)  
    DB[siteID].updated = True

def saveData():
    """
    Save data to the IEM database
    """
    timer_start = mx.DateTime.now()
    updates = 0
    skips = 0
    for key in DB:
        val = DB[key]
        if not val.updated or val.nwsli is None:
            skips += 1
            continue
        val.sanityCheck()
        iem = access.Ob(val.nwsli, val.network)
        val.avgWinds()
        val.ts += mx.DateTime.RelativeDateTime(second=0)
        iem.setObTime(val.ts)
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
        try:
            iem.updateDatabase(None, dbpool=DBPOOL)
            val.updated = False
            updates += 1
        except:
            traceback.print_exc()
            continue
        val.xsped = 0
        del(iem)

    timer_end = mx.DateTime.now()
    print "Time: %.2fs Updates: %s Skips: %s" % ( timer_end - timer_start, 
                                                  updates, skips)                                            

application = service.Application("NWN 2 DB")
serviceCollection = service.IServiceCollection(application)

remoteServerUser = secret.cfg['hubuser']
remoteServerPass = secret.cfg['hubpass']
clientFactory = NWNClientFactory(remoteServerUser,
                                 remoteServerPass)

client = internet.TCPClient(secret.cfg['hubserver'], 
                            secret.cfg['hubport'], clientFactory)
client.setServiceParent( serviceCollection )
LC = LoopingCall( saveData )
LC.start(59)
