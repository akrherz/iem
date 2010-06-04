#!/mesonet/python/bin/python

import mx.DateTime
from pyIEM import iemdb
import sys
i = iemdb.iemdb()
mydb = i['iem']

sts = mx.DateTime.DateTime(2008,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)

sql = "SELECT min(day) as d, astext(geom) as g, station, network from summary_2008 WHERE network ~* 'COOP' GROUP by station, network, g"
rs = mydb.query(sql).dictresult()
for i in range(len(rs)):
  #sql = "SELECT min(day) from summary_2007 WHERE station = '%s' and network = '%s'" % (rs[i]['station'], rs[i]['network'])
  #rs2 = mydb.query(sql).dictresult()
  print rs[i]['station'], rs[i]['d']
  #if (rs2[0]['min'] != "2007-10-01"):
  #  continue

  ts = mx.DateTime.strptime(rs[i]['d'], "%Y-%m-%d")
  if (ts == sts):
    continue
  print rs[i]['station']
  now = mx.DateTime.DateTime(2007,9,1)
  while (now < ts):
    sql = "INSERT into summary_%s(station, geom, network, day) VALUES (\
           '%s', 'SRID=4326;%s','%s','%s')" % (now.year, \
           rs[i]['station'], rs[i]['g'],\
           rs[i]['network'], now.strftime("%Y-%m-%d") )
    mydb.query(sql)
    now += interval
