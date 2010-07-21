# Look into the ASOS database and figure out the start time of various 
# sites for a given network.

import sys
sys.path.insert(0, '../lib')
import db, network
asos = db.connect('asos')
mesosite = db.connect('mesosite')

net = sys.argv[1]

table = network.Table( net )
ids = `tuple(table.sts.keys())`

rs = asos.query("SELECT station, min(valid) from alldata WHERE station in %s GROUP by station ORDER by min ASC" % (ids,)).dictresult()
for i in range(len(rs)):
  print rs[i]
  sql = "UPDATE stations SET archive_begin = '%s' WHERE id = '%s' and network = '%s'" % (
     rs[i]['min'], rs[i]['station'], net)
  mesosite.query( sql )
