# Compute the size of the polygon warnings as event progresses

import numpy, mx.DateTime, sys
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

rs = postgis.query("SELECT distinct wfo from sbw_2008").dictresult()

total_area = numpy.zeros( (len(rs), 50), numpy.float)
cnt = numpy.zeros( (len(rs), 50), numpy.int)

for i in range(len(rs)):
  wfo = rs[i]['wfo']
  # Load up their history!
  rs2 = postgis.query("SELECT issue, expire, area(transform(geom,2163)) / 1000000.0 as area from sbw_2008 WHERE wfo = '%s' and phenomena IN ('SV','TO') and status = 'NEW' ORDER by issue ASC" % (wfo,) ).dictresult()
  previous = mx.DateTime.DateTime(2000,1,1)
  for j in range(len(rs2)):
    sts = mx.DateTime.strptime(rs2[j]['issue'][:16], '%Y-%m-%d %H:%M')
    ets = mx.DateTime.strptime(rs2[j]['expire'][:16], '%Y-%m-%d %H:%M')
    if (sts - previous).minutes > 120:
      event = 0
    else:
      event += 1
    if event > 49:
      previous = ets
      continue
    total_area[i,event] += rs2[j]['area']
    cnt[i,event] += 1

    previous = ets

cnt2 = numpy.ma.masked_values(cnt,0)
for i in range(50):
  az = total_area[:,i] / cnt2[:,i]
  print "%s,%s,%.2f,%.2f" % (i+1, sum(cnt[:,i]), numpy.ma.average(cnt2[:,i]), numpy.ma.average(az))
