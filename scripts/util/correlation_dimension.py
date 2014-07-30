#!/mesonet/python-2.4/bin/python
# Compute Nearest Neighbour

from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

#networkStr = "(network ~* 'ASOS' or network ~* 'AWOS' or network ~* 'RWIS' or network in ('KCCI','KELO','KIMT') or network = 'ISUAG')"
#networkStr = "(network ~* 'ASOS' or network ~* 'AWOS' or network ~* 'RWIS')"
#networkStr = "(network ~* 'ASOS' or network ~* 'AWOS')"
#networkStr = "(network in ('KCCI','KELO','KIMT') )"
#networkStr = "(network ~* 'ASOS' )"
#networkStr = "(network = 'AWOS' )"
#networkStr = "(network = 'ISUAG' )"
networkStr = "(network ~* 'RWIS' )"
# Get a list of stations
sql = "SELECT id from stations WHERE %s and contains('SRID=4326;POLYGON((-97.632 39.651, -97.632 44.319, -89.317 44.319, -89.317 39.651, -97.632 39.651))',geom)" % (networkStr,)
rs = mesosite.query(sql).dictresult()
ids = []
for i in range(len(rs)):
  ids.append( rs[i]['id'] )

for radius in range(10000,300000,10000):
  cnt = 0.0
  tot = 0
  for sid in ids:
    sql = "select count(*) from (SELECT id, distance(transform(geom,26915),\
             (select transform(geom,26915) from stations WHERE id = '%s' LIMIT 1))\
      as distance from stations WHERE contains('SRID=4326;POLYGON((-97.632 39.651, -97.632 44.319, -89.317 44.319, -89.317 39.651, -97.632 39.651))',geom) and online = 't' and %s ) as foo\
      WHERE distance < %s" % (sid, networkStr, radius)
    rs = mesosite.query(sql).dictresult()
  #print sid, rs[0]['id'], rs[0]['distance']
    cnt += 1.0
    tot += rs[0]['count']

  print "%.2f," % ( tot / cnt)
