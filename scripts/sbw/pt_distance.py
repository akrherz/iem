import re
from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

data = {}

rs = postgis.query("""
SELECT wfo, ST_asText(geom) as txt, phenomena, eventid, issue 
from warnings WHERE gtype = 'P' and phenomena IN ('TO') and wfo = 'MPX'
and issue > '2007-10-01' 
"""  ).dictresult()

for i in range(len(rs)):
  if not data.has_key(rs[i]['wfo']):
    data[rs[i]['wfo']] = {'count': 0, 'hits': 0}
  # Find our points
  tokens = re.findall("([\-0-9\.]+) ([0-9\.]+)", rs[i]['txt'])
  for pr in tokens[:-1]:
    rs2 = postgis.query("""
select min(ST_distance(ST_Transform(ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'),
  2163), ST_Transform(ST_exteriorring(ST_geometryn(geom,1)),2163) )) from nws_ugc WHERE wfo = '%s'
    """ % (pr[0], pr[1], rs[i]['wfo']) ).dictresult()
    if rs2[0]['min'] < 2000.:
      data[rs[i]['wfo']]['hits'] += 1
    data[rs[i]['wfo']]['count'] += 1

for wfo in data.keys():
  print '%s,%s,%s,%.3f' % (wfo, data[wfo]['hits'], data[wfo]['count'],
    float(data[wfo]['hits'])/float(data[wfo]['count'])*100.)
