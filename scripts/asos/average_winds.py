# Lets compute average v component

import math, sys

def uv(sped,dir):
  dirr = dir * math.pi / 180.00
  s = math.sin(dirr)
  c = math.cos(dirr)
  u = round(- sped * s, 2)
  v = round(- sped * c, 2)
  return u, v

from pyIEM import iemdb
import Numeric
i = iemdb.iemdb()
asos = i['asos']

sql = "SELECT sknt, drct from t%s WHERE station = 'AMW' and \
  extract(month from valid) = 6  \
  and sknt >= 0 and drct >= 0" % (sys.argv[1],)
rs = asos.query(sql).dictresult()

v = []

for i in range(len(rs)):
  sknt = float(rs[i]['sknt'])
  drct = float(rs[i]['drct'])
  myu, myv = uv(sknt, drct)
  v.append(myv)

print Numeric.average(v) * 1.15
