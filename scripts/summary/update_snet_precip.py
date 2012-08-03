"""
Populate the hourly precip table with snet data
"""
import mx.DateTime
import iemdb
IEM = iemdb.connect('iem')
icursor = IEM.cursor()
icursor2 = IEM.cursor()

def compute(ts):
  sql = """select f2.id, f2.network, n, x from
   (SELECT id, network, min(pday) as n from 
   current_log c, stations t WHERE t.network IN ('KELO','KIMT','KCCI') and valid IN ('%s',
   '%s','%s','%s') and pday >= 0 and t.iemid = c.iemid GROUP by id, network) as f1,
   (SELECT id, network, max(pday) as x from 
   current_log c, stations t WHERE t.network IN ('KELO','KIMT','KCCI') and valid IN ('%s',
   '%s','%s','%s') and pday >= 0 and t.iemid = c.iemid GROUP by id, network) as f2
   WHERE f1.id = f2.id and f1.network = f2.network""" % (
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=56),
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=57),
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=58),
       ts + mx.DateTime.RelativeDateTime(hours=-2, minute=59),
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=56),
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=57),
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=58),
       ts + mx.DateTime.RelativeDateTime(hours=-1, minute=59) )
  icursor.execute( sql )
  for row in icursor:
    x = row[3]
    n = row[2]
    station = row[0]

    phour = x - n
    if phour < 0:
      phour = x
    #print "station: %s MinV: %s MaxV: %s Phour: %s" % (station,n,x,phour)
    sql = "INSERT into hourly_%s values ('%s','%s','%s','%s')" % ( ts.year, 
           station, row[1], ts.strftime("%Y-%m-%d %H:%M"), phour)
    icursor2.execute(sql)

compute( mx.DateTime.now() + mx.DateTime.RelativeDateTime(minute=0, second=0) )

icursor.close()
icursor2.close()
IEM.commit()