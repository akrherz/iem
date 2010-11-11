
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
coop = i['coop']

data = [0]*15 # 7 days before and after

rs = coop.query("SELECT valid, max_precip_yr from climate WHERe station = 'ia0200'").dictresult()
for i in range(len(rs)):
  ts = mx.DateTime.strptime("%s%s" % (rs[i]['max_precip_yr'], rs[i]['valid'][4:]), '%Y-%m-%d')
  for j in range(-7,8):
    idx = j+7
    rs2 = coop.query("""SELECT * from climate WHERE station = 'ia0200' and
          valid = '2000-%s' and max_low_yr = %s""" % ((ts + mx.DateTime.RelativeDateTime(days=j)).strftime("%m-%d"),(ts + mx.DateTime.RelativeDateTime(days=j)).strftime("%Y") )).dictresult()
    if len(rs2) > 0:
      print "HIT!", j, ts
      data[idx] += 1

print data
