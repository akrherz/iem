# Neighborhood Weather Net
# Copyright (C) 2003 Iowa State University
# Written by Daryl Herzmann and Travis B. Hartwell
# 
# This module is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

""" 
This application does a lot of things.
1. Creates a server (nwn format) that clients can connect to...
2. Ingests data...
   a. Connects to Baron to get its data
   b. Watches for wx32 files from KELO (provided by LDM)
   c. Connects to IEM service for KIMT data
   d. Listens for TWI poller connections
"""

#from twisted.internet.app import Application
from twisted.application import service, internet
from twisted.cred import checkers, portal

# Hack around 2.0 problem
from twisted.internet import reactor, base
reactor.installResolver(base.BlockingResolver())

# Import nwnserver stuff!
from nwnserver import server, auth, hubclient, proxyserver, pollerserv, filewatcher
from nwnserver.scripts import mainserver

import secret

# Create the Python Hub application
application = service.Application("PythonHub")
serviceCollection = service.IServiceCollection(application)


#______________________________________________________________________
# 1. Setup hub server!
#  Accepts connects on port 14996
hubServerPasswdFile = './passwords.txt'
proxySiteListPath = './sitelist.csv'
hubServerPort = 14996

# set up Portal
hubServerPortal = portal.Portal(proxyserver.HubProxyRealm(proxySiteListPath))
hubServerPortal.registerChecker(checkers.FilePasswordDB(hubServerPasswdFile))

# Set up Hub server service
hubServerFactory = proxyserver.ProxyHubServerFactory(hubServerPortal,
                  proxyserver.IHubProxyClient)
hubServer = internet.TCPServer(hubServerPort, hubServerFactory)
hubServer.setServiceParent(serviceCollection)

#______________________________________________________________________
# 2a.  Connect to Baron to get their data
#remoteServerIP = 'nwnhub.baronservices.com'
#remoteServerPort = 14996
#remoteServerUser = 'delete'
#remoteServerPass = 'delete'
#
#hubClientFactory = hubclient.HubClientProtocolFactory(remoteServerUser,
#                                                      remoteServerPass,
#                                                      hubServerFactory)
#hubClient = internet.TCPClient(remoteServerIP, 
#                               remoteServerPort, 
#                               hubClientFactory)
#hubClient.setServiceParent(serviceCollection)


#______________________________________________________________________
# 2b.  Watches local wx32 files for changes...
wxpath = '/home/ldm/data/kelo/incoming/'
wxfilespec = 'nwn_%03i.txt'
wxids = [0,1,3,4,5,6,7,8,9,11,13,15,25,49] + range(500,520) + range(900, 950)
wx32 = filewatcher.WX32FileWatcher(wxpath, wxfilespec, wxids, hubServerFactory)


#______________________________________________________________________
# 2c.  Connect to iem for KIMT data
kimtServerIP = 'data2.stormnetlive.com'
kimtServerPort = 15002
kimtServerUser = secret.cfg['kimthubuser']
kimtServerPass = secret.cfg['kimthubpass']
kimtClientFactory = hubclient.HubClientProtocolFactory(kimtServerUser,
                                                        kimtServerPass,
                                                        hubServerFactory)
kimtClient = internet.TCPClient(kimtServerIP, kimtServerPort,
                                 kimtClientFactory)
kimtClient.setServiceParent(serviceCollection)

#______________________________________________________________________
# 2d.  Listen for TWI poller clients
pollerServerPasswdFile = './pollerpasswd.txt'
pollerServerConfigFile = './replacements.csv'
pollerServerPort = 14995
# set up Portal
pollerServerPortal = portal.Portal(pollerserv.PollerRealm(pollerServerConfigFile))
pollerServerPortal.registerChecker(checkers.FilePasswordDB(pollerServerPasswdFile))

# set up factory and listen
pollerServerFactory = pollerserv.PollerServerFactory(pollerServerPortal, hubServerFactory)
pollerServer = internet.TCPServer(pollerServerPort, pollerServerFactory)
pollerServer.setServiceParent(serviceCollection)

import sys
import types

def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1],x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs

def print_top_100():
    for n, c in get_refcounts()[:10]:
        print '%10d %s' % (n, c.__name__)
    reactor.callLater(60, print_top_100)

#reactor.callLater(60, print_top_100)
