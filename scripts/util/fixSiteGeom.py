#  Reload a network into the current IEMAccess table
#  Daryl Herzmann 18 Jun 2003
# 19 Jun 2003	Also update the name

import pg, sys
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']
iem = i['iem']

_SITE = sys.argv[1]

rs = mesosite.query("SELECT * from stations WHERE id = '%s' \
   and network = 'IA_COOP' and online = 't' " % (_SITE) ).dictresult()

for i in range(len(rs)):
  for yr in range(2007,2009):
    station = rs[i]["id"]
    iem.query("UPDATE summary_%s set geom = '%s' WHERE \
      station = '%s' and network = 'IA_COOP' " \
      % (yr, rs[i]["geom"], station ) )
iem.query("UPDATE current set geom = '%s' WHERE \
      station = '%s' and network = 'IA_COOP' " \
      % ( rs[i]["geom"], station ) )



