# Clean up the COOP section of the IEMAccess DB
# Daryl Herzmann 15 Dec 2003

import iemAccess, pg

mydb = pg.connect('mesosite')

rs = iemAccess.iemdb.query("SELECT station, network from current \
    WHERE network ~* 'COOP' and valid < '2000-1-1'").dictresult()

for i in range(len(rs)):
  sid = rs[i]['station']
  mydb.query("UPDATE stations SET online = 'f' WHERE id = '%s' \
   and network = '%s'" % (sid, rs[i]['network']) )
  iemAccess.iemdb.query("DELETE from current WHERE station = '%s' \
   and network = '%s'" % (sid, rs[i]['network']) )
  iemAccess.iemdb.query("DELETE from summary WHERE station = '%s' \
   and network = '%s'" % (sid, rs[i]['network']) )
  iemAccess.iemdb.query("DELETE from current_log WHERE station = '%s' \
   and network = '%s'" % (sid, rs[i]['network']) )

  print sid
