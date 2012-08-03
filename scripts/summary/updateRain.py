"""
Update the pday column
"""
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
icursor2 = IEM.cursor()
import mx.DateTime

now = mx.DateTime.now()
yyyy = now.year

sql = """select foo.iemid, foo.d, sum(rain) from 
  (SELECT s.iemid, date(valid at time zone s.tzname) as d, max(phour) as rain, 
  extract(hour from (valid - '1 minute'::interval)) as hour from current_log c, stations s
  WHERE (s.network IN ('AWOS') or s.network ~* 'ASOS') and c.iemid = s.iemid
  and  date(valid at time zone s.tzname) = date(now() at time zone s.tzname) 
  and phour > 0 
  GROUP by s.iemid, hour, d) as foo JOIN stations s on (s.iemid = foo.iemid)
  GROUP by foo.iemid, d"""

icursor.execute(sql)

for row in icursor:
    sql = """UPDATE summary_%s SET pday = '%s' WHERE iemid = %s 
    and day = '%s'""" % (yyyy, row[2], row[0], row[1]) 
    print sql
    icursor2.execute( sql )
    
icursor2.close()
icursor.close()
IEM.commit()
