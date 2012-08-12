
from pyIEM import iemdb
import mx.DateTime, sys
i = iemdb.iemdb()
asos = i['asos']

maxCnt = 0
for yr in range(1973,2009):
  sts = mx.DateTime.DateTime(yr,1,1)
  ets = sts + mx.DateTime.RelativeDateTime(years=1)
  interval = mx.DateTime.RelativeDateTime(hours=1)
  data = {}
  now = sts
  while (now < ets):
    data[now] = 0
    now += interval

  sql = "SELECT valid, wind_chill(tmpf,sknt) as wc from t%s WHERE \
   station = '%s' and tmpf < 32 and tmpf > -50 and sknt > 0" % (yr, sys.argv[1])
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    wc = float( rs[i]['wc'] )
    if (wc >= int(sys.argv[2])):
      continue
    ts = mx.DateTime.strptime(rs[i]['valid'][:13], '%Y-%m-%d %H')
    data[ts] = 1

  # 
  now = sts
  cnt = 0
  tot_hours = 0
  while (now < ets):
    hrlycnt = 0
    while (data[now]):
      hrlycnt += 1
      tot_hours += 1
      now += interval
    if (hrlycnt > 2):
      cnt += 1
    if (hrlycnt > maxCnt):
      maxCnt = hrlycnt
      print now, maxCnt
    now += interval

  print "%s,%s,%s" % (sts.year, tot_hours, cnt)
