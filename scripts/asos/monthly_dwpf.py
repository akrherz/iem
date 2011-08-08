#!/mesonet/python/bin/python

from pyIEM import iemdb
i = iemdb.iemdb()
asos = i['asos']
coop = i['coop']

for yr in range(1973,2008):
  sql = "select avg(dwpf) from t%s WHERE station = 'DSM' and valid BETWEEN '%s-07-01' and '%s-08-01' and dwpf > 0" % (yr,yr,yr)
  rs = asos.query(sql).dictresult()

  sql = "select rain from r_monthly WHERE stationid = 'ia2203' and monthdate = '%s-07-01'" % (yr,)
  rs2 = coop.query(sql).dictresult()

  print yr, rs[0]['avg'], rs2[0]['rain']
