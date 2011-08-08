#!/mesonet/python/bin/python

from pyIEM import iemdb
import mx.DateTime, sys
i = iemdb.iemdb()
asos = i['asos']


for yr in range(1973,2009):
  hrs = [0,0,0,0]
  sql = "SELECT to_char(valid, 'YYYY-MM-DD HH24') as d, min(wind_chill(tmpf,sknt)) as wc from t%s WHERE \
   station = '%s' and tmpf < 32 and tmpf > -50 and sknt > 0 \
   and valid > '%s-10-01' GROUP by d" % (yr, sys.argv[1], yr)
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    wc = float( rs[i]['wc'] )
    if (wc < -30):
      hrs[0] += 1
    if (wc < -20):
      hrs[1] += 1
    if (wc < -10):
      hrs[2] += 1
    if (wc < 0):
      hrs[3] += 1
  sql = "SELECT to_char(valid, 'YYYY-MM-DD HH24') as d, min(wind_chill(tmpf,sknt)) as wc from t%s WHERE \
   station = '%s' and tmpf < 32 and tmpf > -50 and sknt > 0 \
   and valid < '%s-04-01' GROUP by d" % (yr+1, sys.argv[1], yr+1)
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    wc = float( rs[i]['wc'] )
    if (wc < -30):
      hrs[0] += 1
    if (wc < -20):
      hrs[1] += 1
    if (wc < -10):
      hrs[2] += 1
    if (wc < 0):
      hrs[3] += 1

  print "%s,%s,%s,%s,%s" % (yr, hrs[0],hrs[1],hrs[2],hrs[3])
