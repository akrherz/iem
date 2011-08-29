import sys
from pyIEM import iemdb
import sys
state = sys.argv[1]
import network
nt = network.Table("%sCLIMATE" % (state.upper(),))
i = iemdb.iemdb()
coopdb = i['coop']
mesosite = i['mesosite']

#st.ids = ['IA8266',]
# First we create a dictionary of sites we want to estimate from
friends = {}
for id in st.ids:
  sql = """select id, distance(geom, 'SRID=4326;POINT(%s %s)') from stations
         WHERE network = '%sCLIMATE' and id != '%s' ORDER by distance
         ASC LIMIT 11""" % (st.sts[id]['lon'], st.sts[id]['lat'], state.upper(), id.upper())
  rs = mesosite.query(sql).dictresult()
  friends[id] = "('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" \
          % (rs[0]['id'].lower(), rs[1]['id'].lower(),\
                rs[2]['id'].lower(), rs[3]['id'].lower(), rs[4]['id'].lower(),\
                rs[5]['id'].lower(), rs[6]['id'].lower(), rs[7]['id'].lower(),\
                rs[8]['id'].lower(), rs[9]['id'].lower(), rs[10]['id'].lower())

var = sys.argv[2]
for id in nt.sts.keys():
  sql = "select day from alldata_%s WHERE stationid = '%s' and %s IS NULL \
         and day >= '1893-01-01'" % (state.lower(), id.lower(), var)
  rs = coopdb.query(sql).dictresult()
  for i in range(len(rs)):
    if (i > 0 and i % 1000 == 0):
      print "UPDATE %s" % (i,)
    d = rs[i]['day']
    sql="SELECT avg(%s) as h, stddev(%s) as r from alldata_%s WHERE day = '%s'\
           and stationid IN %s and %s IS NOT NULL" % (var, var, state.lower(), d, friends[id], var)
    rs2 = coopdb.query(sql).dictresult()
    try:
      sdev = float(rs2[0]['r'])
    except:
      print d, 'NDF'
      continue
    if (sdev > 29):
      print d, sdev
      continue
    sql = "UPDATE alldata_%s SET estimated = true, %s = %i WHERE stationid = '%s' and day = '%s'"\
          %(state.lower(), var, float(rs2[0]['h']), id.lower(), d)
    #print sql, sdev
    coopdb.query(sql)
  if (len(rs) > 0):
    print "Processed %s for %s [%s]" % (len(rs), id, var)
