from pyIEM import iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

now = mx.DateTime.now()
yyyy = now.year

rs = iemdb.query("""select station, network, sum(rain) as rain from 
  (SELECT station, network, max(phour) as rain, 
  extract(hour from (valid - '1 minute'::interval)) as hour from current_log 
  WHERE (network IN ('AWOS','DCP') or network ~* 'ASOS') 
  and date(valid) = 'TODAY'::timestamp 
  and phour > 0 
  GROUP by station, network, hour) as foo 
  GROUP by station, network""").dictresult()

for i in range(len(rs)):
	iemdb.query("""UPDATE summary_%s SET pday = '%s' WHERE station 
    = '%s' and day = 'TODAY' and network = '%s'""" % (
    yyyy, rs[i]['rain'], rs[i]['station'], rs[i]['network']) )
