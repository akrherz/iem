# Print out PHP listing of neighbors...
# Daryl Herzmann 23 Apr 2003

from pyIEM import stationTable, iemdb
i = iemdb.iemdb()
mydb = i['mesosite']
st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")


for stid in st.ids:
  sql = "select id, distance(geom,(select geom from stations WHERE id = '%s'))\
    as distance  from stations \
    WHERE online = 't' and network = 'KCCI' and id != '%s' ORDER by distance" % (stid, stid)

  rs = mydb.query(sql).dictresult()

  print "'%s' => Array('%s', '%s', '%s', '%s', '%s')," % (stid, \
    rs[0]['id'], rs[1]['id'], rs[2]['id'], rs[3]['id'], rs[4]['id'])
