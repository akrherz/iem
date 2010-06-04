
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

sdict = {}
rs = mesosite.query("SELECT id, wfo from stations WHERE network ~* 'ASOS'").dictresult()
for i in range(len(rs)):
  sdict[ rs[i]['id'] ] = rs[i]['wfo']

# 
rs = mesosite.query("select s.id, c.wfo, s.network from stations s, cwa c WHERE s.geom && c.the_geom and contains(c.the_geom, s.geom) and s.network ~* 'ASOS' ").dictresult()

for i in range(len(rs)):
  stid = rs[i]['id']
  if (sdict[stid] != rs[i]['wfo']):
    mesosite.query("UPDATE stations SET wfo = '%s' WHERE id = '%s' and network = '%s'" % (rs[i]['wfo'], stid, rs[i]['network']) )
    print 'Conflict %s Old: [%s] New: [%s]' % (stid, sdict[stid], rs[i]['wfo'])
