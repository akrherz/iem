#!/mesonet/python/bin/python
#  RWIS_yest.py
#   - Generates HI/LOW table from the RWIS data
# 21 May 2002:	Daryl Herzmann
# 28 Oct 2002:	Fix column formatting issue for the RWIS data
#  6 Jan 2003:	cleanup, sigh
#  6 Jun 2003	Use indexes in DB searches
#		Go for any date
#		Also print out count of observations
#  6 Sep 2003	round needs to use numberic as an arg!
# 14 Mar 2005	updates
####################################################

import mx.DateTime,  shutil, sys, os
from pyIEM import iemdb, stationTable
i = iemdb.iemdb()
mydb = i["rwis"]
st = stationTable.stationTable("/mesonet/TABLES/RWIS.stns")

o = open('IEMRWISTP.txt','w')
o.write("IEMRWISTP\n")
o.write(";IOWA ENVIRONMENTAL MESONET\n")
o.write(";   RWIS TEMPERATURES\n")
o.write(";   AS CALCULATED ON THE IEM SERVER\n")

if (len(sys.argv) == 4):
  now = mx.DateTime.DateTime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) )
  print "SPECIAL TIME REQUESTED: ", now
else:
  now = mx.DateTime.now() - mx.DateTime.DateTimeDeltaFromDays(1)
  now = now + mx.DateTime.RelativeDateTime(minute=0)
goodDay = now.strftime("%Y-%m-%d")
year = now.strftime("%Y")


o.write(";   VALID FOR 24H LOCAL DAY OF: "+ now.strftime("%d %b %Y") +"\n\n")
o.write("%-5s %-30s %-4s %-4s %-4s\n" % ("ID", "STATION", "HI", "LO", "OBS") )


sql = "SELECT station, count(valid) as obs, \
  round(max(tmpf)::numeric,0) as maxtmpf, round(min(tmpf)::numeric,0) as mintmpf from t%s \
  WHERE date(valid) = '%s' and tmpf > -50 group by station" % (year, now.strftime("%Y-%m-%d"))
rs = mydb.query(sql).dictresult()

for i in range(len(rs)):
  thisStation = rs[i]["station"]
  thisHigh = rs[i]["maxtmpf"]
  thisLow = rs[i]["mintmpf"]
  cnt = rs[i]["obs"]
  o.write("%-5s %-30s %-4i %-4i %-4s\n" % (thisStation, \
   st.sts[thisStation]["name"], thisHigh, thisLow, cnt) )

o.write(".END\n")
o.close()
cmd = "/home/ldm/bin/pqinsert -p 'plot ac %s0000 text/IEMRWISTP.txt IEMRWISTP.txt txt' IEMRWISTP.txt" % (now.strftime("%Y%m%d"), )
os.system(cmd)
