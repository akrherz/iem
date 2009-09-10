#!/mesonet/python/bin/python
# Script to initialize the reports database

import pg, mx.DateTime, string, constants
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
mydb = pg.connect("coop", 'iemdb')

#mydb.query("DELETE from r_monthly")

e = mx.DateTime.DateTime(1951, 1, 1)
interval = mx.DateTime.RelativeDateTime(months=+1)

st.ids = ['IA2364',]
for id in st.ids:
  dbid = string.lower(id)
  s = constants.startts(dbid)
  print dbid, s
  now = s
  while (now < e):
    mydb.query("INSERT into r_monthly(stationid, monthdate) values \
     ('%s', '%s')" % (dbid, now.strftime("%Y-%m-%d") ) )
    now += interval
