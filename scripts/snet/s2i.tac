# Application to save SNET data flow to the IEM Access database!

from nwnserver import hubclient

from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.protocols import policies, basic
from twisted.internet import protocol
#from twisted.internet.app import Application
from twisted.application import service, internet
from twisted.enterprise import adbapi


from sys import stdout
import traceback
import secret
import re, mx.DateTime, sys, os
from pyIEM import mesonet, nwnformat
from pyIEM import iemAccessOb, iemAccess, cameras
iemaccess = iemAccess.iemAccess()


#class NWNClientFactory(protocol.ReconnectingClientFactory):                                        
class NWNClientFactory(hubclient.HubClientProtocolBaseFactory):
    maxDelay = 60.0
    factor = 1.0
    initialDelay = 60.0

    def processData(self, data):
        reactor.callLater(0, ingestData, data)
                   

db = {}                 

def ingestData(data):
  if (data == None or data == ""):
    return

  tokens = re.split("\s+", data)
  if (len(tokens) != 14): 
    return

  siteID = tokens[1]
#  if (tokens[2] != "Min" and tokens[2] != "Max"):
  if (not db.has_key(siteID) ):
    db[siteID] = nwnformat.nwnformat()
    db[siteID].sid = int(siteID)
    db[siteID].updated = 0

  #if (siteID == "507"):
  #  print tokens
  db[siteID].parseLineRT(tokens)  
  db[siteID].updated = 1

def send2ldm():
  out = open('wxc_snet8_cameras.txt', 'w')
  out.write("""Weather Central 001d0300 Surface Data
   7
   5 Station
   3 AirTemp
   3 AirDewp
   3 Wind Direction Degrees
   3 Wind Direction Text
   3 Wind Speed
   6 Today Precip
""")
  for ky in cameras.cams.keys():
    id = "%03i" % (mesonet.snetConvBack[ky],)
    if (not db.has_key(id)): continue
    try:
      out.write("%s %3.0f %3.0f %3.0f %3s %3.0f %6.2f\n" % \
      (ky, float(db[id].tmpf),\
      mesonet.dwpf( db[id].tmpf, db[id].humid), float(db[id].drct),\
      mesonet.drct2dirTxt(db[id].drct),\
      float(db[id].sknt), float(db[id].pDay)) )
    except:
      traceback.print_exc()
      out.write("%s %3s %3s %3s %3s %3s %6s\n" %(ky,'M','M','M','M','M','M') )

  out.close()
  del(out)
  os.system("/home/ldm/bin/pqinsert wxc_snet8_cameras.txt")
  reactor.callLater(10, send2ldm)

def saveData():
  timer_start = mx.DateTime.now()
  updates = 0
  skips = 0
  for key in db.keys():
    sid = int(key)
    # Skip if no updates!  Save time
    if (not db[key].updated):
      #print "Skipped %s" % (key,)
      skips += 1
      continue
    if (mesonet.snetConv.has_key(sid)):
      db[key].sanityCheck()
      #if (mesonet.snetConv[sid] == "SCLS2"):
      #  print db[key].tmpf, db[key].humid
      iem = iemAccessOb.iemAccessOb(mesonet.snetConv[sid])
      db[key].avgWinds()
      db[key].ts += mx.DateTime.RelativeDateTime(second=0)
      iem.setObTime(db[key].ts)
      if (db[key].tmpf == 460):
        iem.data['tmpf'] = -99
        iem.data['relh'] = -99
        iem.data['dwpf'] = -99
      else:
        iem.data['tmpf'] = db[key].tmpf
        iem.data['relh'] = db[key].humid
        iem.data['dwpf'] = mesonet.dwpf( db[key].tmpf, db[key].humid)

      iem.data['drct'] = db[key].avg_drct
      iem.data['sknt'] = db[key].avg_sknt
      iem.data['srad'] = db[key].rad
      iem.data['max_srad'] = db[key].xsrad
      iem.data['pres'] = db[key].pres
      iem.data['pday'] = db[key].pDay
      iem.data['pmonth'] = db[key].pMonth
      iem.data['gust'] = float(db[key].xsped) * 0.86897
      #if (mesonet.snetConv[sid] == "SFCM5"):
      #  print key, db[key].xsped, iem.data['gust']
      iem.data['max_drct'] = db[key].xdrct
      try:
        #iem.updateDatabase(None, dbpool)
        iem.updateDatabase(iemaccess)
        db[key].updated = 0
        updates += 1
      except:
        traceback.print_exc()
        continue
      db[key].xsped = 0
      del(iem)

  timer_end = mx.DateTime.now()
  print "Time: %.2fs Updates: %s Skips: %s" % ( timer_end - timer_start, updates, skips)
  reactor.callLater(56, saveData)                                               

application = service.Application("NWN 2 DB")
serviceCollection = service.IServiceCollection(application)

remoteServerUser = secret.cfg['hubuser']
remoteServerPass = secret.cfg['hubpass']
clientFactory = NWNClientFactory(remoteServerUser,
                                 remoteServerPass)

client = internet.TCPClient('127.0.0.1', 14996, clientFactory)
client.setServiceParent( serviceCollection )

reactor.callLater(6, saveData)
#reactor.callLater(10, send2ldm)
