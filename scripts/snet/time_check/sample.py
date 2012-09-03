# Application to save SNET data flow to the IEM Access database!
# Daryl Herzmann 4 Sept 2003
# 16 Sep 2003	Must be careful how we import IEMAccessOb
#		Don't ingest Max and Min lines

from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.protocols import policies, basic
from twisted.internet import protocol
from twisted.application import service, internet
from sys import stdout                                                         
from pyIEM import nwnformat, mesonet,stationTable
import re
import mx.DateTime

from nwnserver import hubclient


st = stationTable.stationTable("/mesonet/TABLES/snet.stns")

#class NWNClientProtocol(basic.LineReceiver):
#    def lineReceived(self, line):
#        #self.resetTimeout()
#        self.factory.processData(line)


                                                                                
class NWNClientFactory(hubclient.HubClientProtocolBaseFactory):
    #protocol = NWNClientProtocol                         
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
  if (tokens[2] != "Min" and tokens[2] != "Max"):
    if (not db.has_key(siteID) ):
      db[siteID] = nwnformat.nwnformat()
    db[siteID].raw = tokens
    db[siteID].parseLineRT(tokens)  

                                                                   
def saveData():
  out = open('times.txt', 'w')
  for key in db.keys():
    sid = int(key)
    now = mx.DateTime.now()
    if (mesonet.snetConv.has_key(sid)):
      t = db[key].raw[2]
      d = db[key].raw[3]
      ts = mx.DateTime.strptime(t +" "+d, "%H:%M %m/%d/%y")
      out.write("%s|%s|%.1f\n" % (mesonet.snetConv[sid], st.sts[ mesonet.snetConv[sid]]["name"], (now - ts)) )

  out.close()
  reactor.stop()

application = service.Application("PythonHub")
serviceCollection = service.IServiceCollection(application)

nwn =  NWNClientFactory('sall999', 'sall999')

cli = internet.TCPClient('127.0.0.1', 14996, nwn )
cli.setServiceParent(serviceCollection)
reactor.callLater(120, saveData)

