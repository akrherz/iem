from pyIEM import iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

now = mx.DateTime.now()
yyyy = now.year

rs = iemdb.query("""select station, network, sum(rain) as rain from 
  (SELECT station, s.network, max(phour) as rain, 
  extract(hour from (valid - '1 minute'::interval)) as hour from current_log c, stations s
  WHERE (c.network IN ('AWOS') or c.network ~* 'ASOS') and c.network = s.network
  and  date(valid at time zone s.tzname) = date(now() at time zone s.tzname) 
  and phour > 0 
  GROUP by station, s.network, hour) as foo 
  GROUP by station, network""").dictresult()

for i in range(len(rs)):
	iemdb.query("""UPDATE summary_%s SET pday = '%s' WHERE station 
    = '%s' and day = 'TODAY' and network = '%s'""" % (
    yyyy, rs[i]['rain'], rs[i]['station'], rs[i]['network']) )
