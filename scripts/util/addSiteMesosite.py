
import sys, mx.DateTime
from pyIEM import iemdb, iemAccess
i = iemdb.iemdb()
mesosite = i['mesosite']
iemaccess = iemAccess.iemAccess()

_NETWORK = sys.argv[1]
_ID = sys.argv[2]

rs = mesosite.query("SELECT * from stations WHERE network = '%s' \
   and online = 't' and id = '%s' " % (_NETWORK, _ID) ).dictresult()

#iemAccess.iemdb.query("BEGIN;")
#iemAccess.iemdb.query("DELETE from current WHERE network = '%s'" % (_NETWORK) )

for i in range(len(rs)):
  station = rs[i]["id"]
  print "Adding station :%s:" % (station,)
#  try:
  iemaccess.iemdb.query("INSERT into current(station, geom, network, sname)\
      VALUES ('%s', setsrid('%s'::geometry, 4326), '%s', '%s') " \
      % (station, rs[i]["geom"], _NETWORK, rs[i]["name"] ) )
  iemaccess.iemdb.query("INSERT into summary_%s(station, geom, network, day)\
      VALUES ('%s', setsrid('%s'::geometry, 4326), '%s', '%s') " \
      % (mx.DateTime.now().year, station, rs[i]["geom"], _NETWORK, 'TODAY' ) )
  iemaccess.iemdb.query("INSERT into trend_1h(station, geom, network)\
      VALUES ('%s', setsrid('%s'::geometry, 4326), '%s') " \
      % (station, rs[i]["geom"], _NETWORK) )
  iemaccess.iemdb.query("INSERT into trend_15m(station, geom, network)\
      VALUES ('%s', setsrid('%s'::geometry, 4326), '%s') " \
      % (station, rs[i]["geom"], _NETWORK) )
#  except:
#    print "Possible Dup! :%s:" % (station,)

#iemAccess.iemdb.query("END;")


