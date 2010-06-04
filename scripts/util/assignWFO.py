
from pyIEM import iemdb
import re
i = iemdb.iemdb()
mydb = i["mesosite"]

rs = mydb.query("select s.id, c.wfo from stations s, cwa c WHERE \
  s.geom && c.the_geom and contains(c.the_geom, s.geom) \
  and s.wfo IS NULL").dictresult()

for i in range(len(rs)):
  id = rs[i]['id']
  wfo = re.sub("'", " ", rs[i]['wfo'])
  print id, wfo
  mydb.query("UPDATE stations SET wfo = '%s' WHERE id = '%s'" \
   % (wfo, id) )
