
from pyIEM import iemdb
import re
i = iemdb.iemdb()
mydb = i["mesosite"]

rs = mydb.query("select s.id, c.name from stations s, counties c WHERE \
  s.geom && c.the_geom and s.county IS NULL").dictresult()

for i in range(len(rs)):
  id = rs[i]['id']
  cnty = re.sub("'", " ", rs[i]['name'])
  print id, cnty
  mydb.query("UPDATE stations SET county = '%s' WHERE id = '%s'" \
   % (cnty, id) )
