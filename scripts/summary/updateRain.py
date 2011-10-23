from pyIEM import iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

now = mx.DateTime.now()
yyyy = now.year

rs = iemdb.query("""select iemid, sum(rain) as rain from 
  (SELECT s.iemid, max(phour) as rain, 
  extract(hour from (valid - '1 minute'::interval)) as hour from current_log c, stations s
  WHERE (s.network IN ('AWOS') or s.network ~* 'ASOS') and c.iemid = s.iemid
  and  date(valid at time zone s.tzname) = date(now() at time zone s.tzname) 
  and phour > 0 
  GROUP by s.iemid, hour) as foo 
  GROUP by iemid""").dictresult()

for i in range(len(rs)):
	iemdb.query("""UPDATE summary_%s SET pday = '%s' WHERE iemid
    = %s and day = 'TODAY'""" % (
    yyyy, rs[i]['rain'], rs[i]['iemid']) )
