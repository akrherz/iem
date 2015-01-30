""" Figure out the online percentage of schoolnet sites"""

import mx.DateTime
from pyIEM import iemdb 
i = iemdb.iemdb()
snet = i['snet']
mesosite = i['mesosite']

sts = {}
rs = mesosite.query("SELECT * from stations WHERE network = 'KCCI'").dictresult()
for i in range(len(rs)):
  sts[ rs[i]['id'] ] = rs[i]

rs = snet.query("SELECT station, count(*) from alldata WHERE valid > '2007-01-01' and valid < '2008-01-01' GROUP by station").dictresult()

obs = 0
for i in range(len(rs)):
  if sts.has_key( rs[i]['station'] ):
    sts[ rs[i]['station'] ]['has'] = 1
    obs += rs[i]['count']

ts0 = mx.DateTime.DateTime(2008,1,1)
ts1 = mx.DateTime.DateTime(2009,1,1)
full = int( (ts1 - ts0).minutes )

total = 0
for id in sts.keys():
  if sts[id].has_key('has'):
    total += full

print float(obs) / float(total) * 100.0
print total / full

