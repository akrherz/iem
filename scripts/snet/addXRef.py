#!/mesonet/python-2.4/bin/python
# Need something to add in locs and counties not previously there...

from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']
postgis = i['postgis']
kcci = i['kcci']

rs = mesosite.query("SELECT * from stations WHERE network = 'KCCI' and online = 't'").dictresult()

for i in range(len(rs)):
  sid = rs[i]["id"]
  county = rs[i]["county"]
  sql = "SELECT ugc from nws_ugc WHERE \
    name = '%s' and wfo = 'DMX' and polygon_class = 'C'" % (county,)
  rs2 = postgis.query(sql).dictresult()
  fips = "%s%s" % ('19', rs2[0]['ugc'][3:])
  kcci.query("DELETE from xref WHERE sid = '%s'" % (sid,))
  kcci.query("INSERT into xref(sid, fips, cname) values ('%s', %s, '%s')" % \
    (sid, fips, county) )
