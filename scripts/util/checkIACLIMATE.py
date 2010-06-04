
from pyIEM import iemdb 
i = iemdb.iemdb()
mesosite = i['mesosite']
coop = i['coop']

rs = mesosite.query("select id, name from stations WHERE network = 'COOPDB' and id NOT IN (select id from stations WHERE network = 'IACLIMATE') ORDER by id ASC").dictresult()
for i in range(len(rs)):
  id = rs[i]['id']
  rs2 = coop.query("SELECT min(day), max(day) from alldata WHERe stationid = '%s'" % (id.lower(),)).dictresult()
  print id, rs[i]['name'], rs2[0]['min'], rs2[0]['max']
