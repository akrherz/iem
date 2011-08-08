#!/mesonet/python/bin/python

from pyIEM import iemdb
import mx.DateTime, sys
i = iemdb.iemdb()
asos = i['asos']

minLow = 0

for yr in range(1973,2009):

  sql = "SELECT tmpf, sknt, valid, wind_chill(tmpf,sknt) as wc from t%s WHERE \
   station = '%s' and tmpf < 32 and tmpf > -50 and sknt > 0" % (yr, sys.argv[1])
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    wc = float( rs[i]['wc'] )
    if (wc < minLow):
      #print wc, rs[i]['valid'], rs[i]['tmpf'], rs[i]['sknt']
      minLow = wc
    if (wc < -40):
      print wc, rs[i]['valid'], rs[i]['tmpf'], rs[i]['sknt']
