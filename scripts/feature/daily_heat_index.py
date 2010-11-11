
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']

import mx.DateTime
data = {}
sts = mx.DateTime.DateTime(2010,7,1)
ets = mx.DateTime.DateTime(2010,8,17)
interval = mx.DateTime.RelativeDateTime(days=1)

now = sts
while now < ets:
  data[now.strftime("%Y%m%d")] = [0]*24
  now += interval

rs = asos.query("SELECT valid, tmpf, dwpf from t2010 WHERE station = 'DSM' and valid > '2010-07-01' ORDER by valid ASC").dictresult()
for i in range(len(rs)):
  ts = mx.DateTime.strptime(rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
  h = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']))
  data[ ts.strftime("%Y%m%d") ][ ts.hour ] = h

sts = mx.DateTime.DateTime(2010,7,1)
ets = mx.DateTime.DateTime(2010,8,17)
interval = mx.DateTime.RelativeDateTime(days=1)

now = sts
while now < ets:
  lkp = now.strftime("%Y%m%d")
  sz = 24.0
  cln = []
  for v in data[lkp]:
    if v != 0:
      cln.append(v)
  print "%s,%.2f,%.2f,%.2f" % (now.strftime("%Y-%m-%d"), max(cln), sum( cln ) / float(len(cln)), min(cln) )
  now += interval
