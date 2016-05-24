# Compute the size of the polygon warnings as we load up on events, tricky

import numpy, mx.DateTime, sys
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

rs = postgis.query("SELECT distinct wfo from sbw_2009").dictresult()

total_area = numpy.zeros( (len(rs), 10), numpy.float)
cnt = numpy.zeros( (len(rs), 10), numpy.int)

big = {}

for i in range(len(rs)):
  wfo = rs[i]['wfo']
  # Load up their history!
  rs2 = postgis.query("SELECT issue, expire, area(transform(geom,2163)) / 1000000.0 as area from sbw_2009 WHERE wfo = '%s' and phenomena IN ('SV','TO') and status = 'NEW' ORDER by issue ASC" % (wfo,) ).dictresult()
  previous = mx.DateTime.DateTime(2000,1,1)
  for j in range(len(rs2)):
    sts = mx.DateTime.strptime(rs2[j]['issue'][:16], '%Y-%m-%d %H:%M')
    ets = mx.DateTime.strptime(rs2[j]['expire'][:16], '%Y-%m-%d %H:%M')
    # Look around in time
    events = 0
    for k in range(j-10,j+10):
      if k < 0 or k >= len(rs2) or k == 0:
        continue
      _sts = mx.DateTime.strptime(rs2[k]['issue'][:16], '%Y-%m-%d %H:%M')
      _ets = mx.DateTime.strptime(rs2[k]['expire'][:16], '%Y-%m-%d %H:%M')
      if _ets > sts and _sts < sts:
        events += 1
    if events > 9:
      if not big.has_key(wfo): big[wfo] = 0
      big[wfo] += 1
      events = 9

    total_area[i,events] += rs2[j]['area']
    cnt[i,events] += 1


print big
cnt2 = numpy.ma.masked_values(cnt,0)
for i in range(10):
  az = total_area[:,i] / cnt2[:,i]
  print "%s,%s,%.2f,%.2f" % (i+1, sum(cnt[:,i]), numpy.ma.average(cnt2[:,i]), numpy.ma.average(az))
