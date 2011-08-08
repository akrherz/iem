#!/mesonet/python/bin/python

from pyIEM import iemdb, mesonet
import mx.DateTime, sys
i = iemdb.iemdb()
asos = i['asos']

minLow = 0

for yr in range(1973,2010):

  sql = "SELECT dwpf, tmpf, valid  from t%s WHERE \
   station = '%s' and dwpf >= 70" % (yr, sys.argv[1])
  rs = asos.query(sql).dictresult()
  for i in range(len(rs)):
    hdex = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']) )
    if hdex > 100:
      print rs[i]['valid'], hdex, rs[i]['tmpf'], rs[i]['dwpf']
