
from pyIEM import iemdb
i = iemdb.iemdb()
asos = i['asos']

data = {}

for yr in range(1973,2008):
  sql = "SELECT drct, sknt from t%s WHERE station = 'DSM' and sknt > 25 \
         and extract(month from valid) = 4" % (yr,)
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    drct = rs[i]['drct']
    sknt = rs[i]['sknt']
    if not data.has_key(drct):
      data[drct] = 0

    data[drct] += 1

keys = data.keys()
keys.sort()

for k in keys:
  print k, data[k]
