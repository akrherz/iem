
import mx.DateTime
from pyIEM import iemdb
i = iemdb.iemdb()
iem = i['iem']

def compute(ts):
  sql = "select f2.station, f2.network, n, x from \
   (SELECT station, network, min(pday) as n from \
   current_log WHERE network IN ('KELO','KIMT','KCCI') and valid IN ('%s',\
   '%s','%s','%s') and pday >= 0 GROUP by station, network) as f1,\
   (SELECT station, network, max(pday) as x from \
   current_log WHERE network IN ('KELO','KIMT','KCCI') and valid IN ('%s',\
   '%s','%s','%s') and pday >= 0 GROUP by station, network) as f2\
   WHERE f1.station = f2.station and f1.network = f2.network"\
   % ( ts + mx.DateTime.RelativeDateTime(hours=-2, minute=56),\
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=57),\
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=58),\
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=59),\
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=56),\
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=57),\
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=58),\
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=59) )
  rs = iem.query(sql).dictresult()
  for i in range(len(rs)):
    x = rs[i]['x']
    n = rs[i]['n']
    station = rs[i]['station']

    phour = x - n
    if (phour < 0):
      phour = rs[i]['x']
    #print "station: %s MinV: %s MaxV: %s Phour: %s" % (station,n,x,phour)
    sql = "INSERT into hourly_%s values ('%s','%s','%s','%s')" % ( ts.year, \
           station, rs[i]['network'], ts.strftime("%Y-%m-%d %H:%M"), phour)
    iem.query(sql)

compute( mx.DateTime.now() + mx.DateTime.RelativeDateTime(minute=0, second=0) )

#sts = mx.DateTime.DateTime(2008,7,24,1)
#ets = mx.DateTime.DateTime(2008,7,25,8)
#interval = mx.DateTime.RelativeDateTime(hours=1)
#now = sts
#while (now < ets):
#  compute( now )
#  now += interval
