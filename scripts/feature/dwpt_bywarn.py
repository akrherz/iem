# Extract Dwpt by warning

import mx.DateTime
from pyIEM import iemdb, stationTable
i = iemdb.iemdb()
postgis = i["postgis"]
asos = i["asos"]
st = stationTable.stationTable("/mesonet/TABLES/iowa.stns")

output = open('month_dwpf.csv', 'w')

for year in range(1986,2011):
  print year
  rs = postgis.query("""select x(c) as lon, y(c) as lat, 
     extract(month from issue) as month, issue, phenomena from 
       (select st_centroid(st_union(geom)) as c, wfo, phenomena, eventid, 
        issue from warnings_%s WHERE ugc ~* '^IAC' and 
        phenomena in ('TO','SV') and significance ='W' and gtype = 'C' 
        GROUP by issue, phenomena, eventid, wfo) as foo""" % (year,)
      ).dictresult()
  for i in range(len(rs)):
    lat = rs[i]['lat']
    lon = rs[i]['lon']
    month = rs[i]['month']
    phenomena = rs[i]['phenomena']
    ts = mx.DateTime.strptime(rs[i]['issue'][:16], '%Y-%m-%d %H:%M')

    obs = asos.query("""SELECT * from t%s where valid BETWEEN '%s' and '%s'
      and station in %s and dwpf > 0 and tmpf > 0 ORDER by valid ASC""" % (year, 
    (ts - mx.DateTime.RelativeDateTime(minutes=60)).strftime("%Y-%m-%d %H:%M"),
    (ts + mx.DateTime.RelativeDateTime(minutes=10)).strftime("%Y-%m-%d %H:%M"),
    `tuple(st.ids)`)).dictresult()
    dist = 1000
    val = None
    for j in range(len(obs)):
      slat = st.sts[obs[j]['station']]['lat']
      slon = st.sts[obs[j]['station']]['lon']
      sdist = ((slat - lat)**2 + (slon - lon)**2)**.5
      if slon < lon and slat > lat and sdist > 0.2: # Nothing NW please
        continue
      if sdist < dist:
        dist = sdist
        val = obs[j]
    if val:
      output.write("%s,%s,%s,%.3f,%s,%s\n" % (month, val['dwpf'], phenomena, dist, val['tmpf'] - val['dwpf'], ts.strftime("%Y-%m-%d %H:%M")))

output.close()
