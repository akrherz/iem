#!/mesonet/python/bin/python

import mx.DateTime, sys, iemdb
i = iemdb.iemdb()
mydb = i['scan']

y = int(sys.argv[1])
m = int(sys.argv[2])
d = int(sys.argv[3])
now = mx.DateTime.DateTime(y,m,d)

stids = {2031: 'Ames', 2068: 'Shagbark', 2001: 'Rogers Farm', 2047: 'Spickard', 2004: 'Mason'}

for id in stids.keys():
  sql = "SELECT valid, srad from t%s_hourly WHERE station = %s and date(valid) \
 = '%s' ORDER by valid ASC" % (now.year, id, now.strftime("%Y-%m-%d"))
  rs = mydb.query(sql).dictresult()
  for i in range(len(rs)):
    print "%s,%s,%s,%s" % (id, stids[id], rs[i]['valid'], rs[i]['srad'])
