#!/mesonet/python/bin/python

import stationTable, mesonet
import pg

st = stationTable.stationTable("/mesonet/TABLES/kcci.stns")
mydb = pg.connect("mesosite")

for id in mesonet.kcci.keys():
  sid = mesonet.kcci[id]
  rs = mydb.query("SELECT * from stations WHERE network = 'KCCI' and id = '%s'" % (sid,) ).dictresult()
  print "%s 300 %.0f %.0f %s" % (id, rs[0]["latitude"] * 1000000, rs[0]["longitude"] * 1000000, st.sts[ mesonet.kcci[id] ]["name"])

