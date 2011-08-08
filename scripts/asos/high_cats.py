#!/mesonet/python/bin/python

from pyIEM import iemdb
i = iemdb.iemdb()
asos = i['coop']

for yr in range(1894,2008):
  rs = asos.query("select ((high +70)::int / 10) -7 as a, count(*) from alldata WHERE stationid = 'ia0200' and ((year = %s and month in (1,2)) or (year = %s and month in (12))) GROUP by a ORDER by a ASC" % (yr+1, yr) ).dictresult()
  data = {-1:0,0:0,1:0,2:0,3:0,4:0,5:0,6:0}
  for i in range(len(rs)):
   data[ int(rs[i]['a']) ] = rs[i]['count']
  print "\n%s," % (yr,),
  for q in range(-1,7):
    print "%s," % (data[q],),
