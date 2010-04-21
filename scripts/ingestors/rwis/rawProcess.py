# Script that processes the raw RWIS data into something usable
#  3 Dec 2002:	Use IEM python2.2
# 19 Nov 2003	Put this into a Main()

import rnetwork, sys, os

def Main():
  rn = rnetwork.rnetwork("/mesonet/data/incoming/rwis/rwis.txt", \
    "/mesonet/data/incoming/rwis/rwis_sf.txt")

  #rn.doSF()

  f = open("/mesonet/data/metar/rwis.sao",'w')
  rn.genMETAR(f)
  f.close()

  f = open("/mesonet/data/metar/rwis2.sao",'w')
  rn.genMETAR2(f)
  f.close()

  #rn.currentWriteCDF()

  g = open("rwis.csv",'w')
  rn.currentWriteCDFNWS(g)
  g.close()
  os.system("/home/ldm/bin/pqinsert -p 'plot c 000000000000 csv/rwis.csv bogus csv' rwis.csv")

#  rn.writeNWS()

  rn.updateIEMAccess()

Main()
