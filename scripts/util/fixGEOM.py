#!/mesonet/python/bin/python
#  Reload a network into the current IEMAccess table
#  Daryl Herzmann 18 Jun 2003
# 19 Jun 2003	Also update the name

import pg, sys
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']
iem = i['iem']

rs = mesosite.query("SELECT * from stations WHERE network = 'PO_ASOS' \
   and id = 'PTPN'").dictresult()

for i in range(len(rs)):
  for yr in range(2010,2011):
    station = rs[i]["id"]
    iem.query("UPDATE summary_%s set geom = '%s' WHERE \
      station = '%s'" \
      % (yr, rs[i]["geom"], station ) )

  iem.query("UPDATE current set geom = '%s' WHERE \
      station = '%s'" \
      % (rs[i]["geom"], station ) )


