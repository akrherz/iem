
from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']

import mx.DateTime

sts = mx.DateTime.DateTime(2000,7,1)
ets = mx.DateTime.DateTime(2000,8,17)
hrs = (ets - sts).hours

rs = asos.query("SELECT valid, tmpf, dwpf from alldata WHERE station = 'DSM' and tmpf > 50 and dwpf > 0 and extract(doy from valid) < extract(doy from 'TOMORROW'::date) and extract(month from valid) in (7,8) ORDER by valid ASC").dictresult()
yrtot = 0
ots = mx.DateTime.DateTime(1950,1,1)
for i in range(len(rs)):
  ts = mx.DateTime.strptime(rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
  if ots.year != ts.year:
    print "%s,%.2f" % (ots.year, yrtot / hrs)
    yrtot = 0
  if ots.strftime("%Y%m%d%H") != ts.strftime("%Y%m%d%H"):
    h = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']))
    if h > rs[i]['tmpf']:
      yrtot += (h - rs[i]['tmpf'])
  ots = ts

print "%s,%.2f" % (ots.year, yrtot / hrs)
