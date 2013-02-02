# Script to initialize the reports database

import pg, mx.DateTime, string, constants
import network
nt = network.Table(('ILCLIMATE', 'INCLIMATE','IACLIMATE',
         'OHCLIMATE','MICLIMATE','KYCLIMATE','WICLIMATE','MNCLIMATE',
         'SDCLIMATE','NDCLIMATE','NECLIMATE','KSCLIMATE','MOCLIMATE'))
mydb = pg.connect("coop", 'iemdb')

#mydb.query("DELETE from r_monthly")

s = mx.DateTime.DateTime(2012, 1, 1)
e = mx.DateTime.DateTime(2013, 1, 1)
interval = mx.DateTime.RelativeDateTime(months=+1)

for id in nt.sts.keys():
#for n in range(0,1):
  #for st in ['ND','SD','NE','KS','MO','IL','IN', 'OH','MI','WI','MN','KY','IA']:
  #for st in ['KY',]:
    #dbid = "%s0%03i" % (st, n)
    dbid = id
    if not nt.sts.has_key(dbid.upper()):
      continue
    #s = constants.startts(dbid)
    print dbid, s
    now = s
    while (now < e):
      mydb.query("INSERT into r_monthly(station, monthdate) values \
     ('%s', '%s')" % (dbid, now.strftime("%Y-%m-%d") ) )
      now += interval
