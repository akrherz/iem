#!/mesonet/python-2.4/bin/python
# Compute Nearest Neighbour

from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

st = stationTable.stationTable("/mesonet/TABLES/ia_main.stns")
networks = "('IA_ASOS', 'AWOS', 'IA_RWIS','KCCI','ISUAG')"

cnt = 0.0
tot = 0
for sid in st.ids:
  sql = "SELECT id, distance(transform(geom,26915),\
             (select transform(geom,26915) from stations WHERE id = '%s' LIMIT 1))\
      as distance from stations WHERE online = 't' and network IN %s\
      and id != '%s' ORDER by distance LIMIT 1" % (sid, networks, sid)
  rs = mesosite.query(sql).dictresult()
  #print sid, rs[0]['id'], rs[0]['distance']
  cnt += 1.0
  tot += rs[0]['distance']

print tot / cnt
