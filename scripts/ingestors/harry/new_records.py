import sys
import pg, mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
mydb = i['coop']

sts = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), 1)
ets = sts + mx.DateTime.RelativeDateTime(months=1)

cnt = {'climate': {'max_high': 0, 'min_high': 0, 'max_low': 0, 'min_low': 0, 'max_precip': 0},
       'climate51': {'max_high': 0, 'min_high': 0, 'max_low': 0, 'min_low': 0, 'max_precip': 0}
      }

def update(tbl, col, val, yr, station, valid):
  sql = "UPDATE %s SET %s = %s, %s_yr = %s WHERE station = '%s' and \
       valid = '%s'" % (tbl, col, val, col, yr, station, valid)
  mydb.query(sql)
  cnt[tbl][col] += 1

for tbl in ['climate51','climate']:
  # Load up records
  sql = "SELECT * from %s" % (tbl,)
  rs = mydb.query(sql).dictresult()
  records = {}
  for i in range(len(rs)):
    station = rs[i]['station']
    if (not records.has_key(station)):
      records[station] = {}
    records[station][rs[i]['valid']] = rs[i]

  # Now, load up obs!
  sql = "SELECT * from alldata WHERE day >= '%s' and day < '%s'" % \
        (sts.strftime("%Y-%m-%d"), ets.strftime("%Y-%m-%d") )
  rs = mydb.query(sql).dictresult()
  for i in range(len(rs)):
    dkey = "2000-%s" % (rs[i]['day'][5:], )
    stid = rs[i]['stationid']
    if (not records.has_key(stid)):
      continue
    r = records[stid][dkey]
    if (float(rs[i]['high']) > r['max_high']):
      #print "NEW RECORD MAX HIGH [%s,%s] NEW %s OLD %s" % (stid, rs[i]['day'], rs[i]['high'], r['max_high'])
      update(tbl, 'max_high', rs[i]['high'], rs[i]['day'][:4], stid, dkey)

    if (float(rs[i]['high']) < r['min_high']):
      #print "NEW RECORD MIN HIGH [%s,%s] NEW %s OLD %s" % (stid, rs[i]['day'], rs[i]['high'], r['min_high'])
      update(tbl, 'min_high', rs[i]['high'], rs[i]['day'][:4], stid, dkey)

    if (float(rs[i]['low']) > r['max_low']):
      #print "NEW RECORD MAX LOW [%s,%s] NEW %s OLD %s" % (stid, rs[i]['day'], rs[i]['low'], r['max_low'])
      update(tbl, 'max_low', rs[i]['low'], rs[i]['day'][:4], stid, dkey)

    if (float(rs[i]['low']) < r['min_low']):
      #print "NEW RECORD MIN LOW [%s,%s] NEW %s OLD %s" % (stid, rs[i]['day'], rs[i]['low'], r['min_low'])
      update(tbl, 'min_low', rs[i]['low'], rs[i]['day'][:4], stid, dkey)

    if (float(rs[i]['precip']) > r['max_precip']):
      #print "NEW RECORD MAX RAIN [%s,%s] NEW %s OLD %s" % (stid, rs[i]['day'], rs[i]['precip'], r['max_precip'])
      update(tbl, 'max_precip', rs[i]['precip'], rs[i]['day'][:4], stid, dkey)

print cnt
