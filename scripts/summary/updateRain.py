# 9 Oct 2003	Include the other ASOS networks
# 15 Jun 2004	Local day!
# 10 Feb 2005	Fix summary table

from pyIEM import iemAccess, iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

now = mx.DateTime.now()
yyyy = now.year

rs = iemdb.query("select station, sum(rain) as rain from \
  (SELECT station, max(phour) as rain, \
  extract(hour from valid) as hour from current_log \
  WHERE (network IN ('AWOS','DCP') or network ~* 'ASOS') \
  and date(valid) = 'TODAY'::timestamp \
  and phour > 0 \
  GROUP by station,hour) as foo \
  GROUP by station").dictresult()

for i in range(len(rs)):
	iemdb.query("UPDATE summary_%s SET pday = '%s' WHERE station \
    = '%s' and day = 'TODAY' " % (yyyy, rs[i]['rain'], rs[i]['station']) )
