#!/mesonet/python/bin/python
# Script to initialize the reports database

import pg, mx.DateTime, string
from pyIEM import stationTable
st = stationTable.stationTable("/mesonet/TABLES/coopClimate.stns")
mydb = pg.connect("coop", 'iemdb')


s = mx.DateTime.DateTime(1893, 1, 1)
e = mx.DateTime.DateTime(1951, 1, 1)
interval = mx.DateTime.RelativeDateTime(months=+1)

#for id in st.ids:
for dbid in ['ia2364']:
  now = s
  while (now < e):
    mydb.query("INSERT into r_monthly(station, monthdate) values \
     ('%s', '%s')" % (dbid, now.strftime("%Y-%m-%d") ) )
    now += interval
