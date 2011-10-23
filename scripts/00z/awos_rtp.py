# 0z version
# 

import  mx.DateTime, shutil, string, os
from pyIEM import iemAccessDatabase, stationTable
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")
iemaccess = iemAccessDatabase.iemAccessDatabase()
iemaccess.query("SET TIME ZONE 'GMT'")


ets = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(hour=0,minute=0)
sts12z = ets + mx.DateTime.RelativeDateTime(hours=-12)
sts6z = ets + mx.DateTime.RelativeDateTime(hours=-18)
sts24h = ets + mx.DateTime.RelativeDateTime(days=-1)

#CWI   :CLINTON ARPT       :  79 /  64 /     M /    M /  M
fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

out = open("/tmp/awos_rtp.shef", 'w')
out.write("""


.BR DMX %s Z DH00/TAIRZS/TAIRZI/PP/SF/SD
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   06Z TO 00Z HIGH TEMPERATURE FOR %s
:   06Z TO 00Z LOW TEMPERATURE FOR %s
:   00Z YESTERDAY TO 00Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
""" % ( ets.strftime("%m%d"), 
	string.upper(sts12z.strftime("%d %b %Y")),
	string.upper(sts12z.strftime("%d %b %Y")) ) )

# We get 18 hour highs
highs = {}
sql = "SELECT t.id as station, \
	round(max(tmpf)::numeric,0) as max_tmpf, \
	count(tmpf) as obs FROM current_log c, stations t\
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid > '%s' \
        and valid < '%s' \
	and tmpf > -99 GROUP by t.id " % \
	(sts6z.strftime("%Y-%m-%d %H:%M"),
         ets.strftime("%Y-%m-%d %H:%M") )
rs = iemaccess.query(sql).dictresult()
for i in range(len(rs)):
	highs[ rs[i]["station"] ] = int(rs[i]["max_tmpf"])


# 12z to 12z precip
pcpn = {}
rs = iemaccess.query("select id as station, sum(precip) from \
		(select t.id, extract(hour from valid) as hour, \
		max(phour) as precip from current_log c, stations t WHERE t.network = 'AWOS' and t.iemid = c.iemid \
		and valid  >= '%s' and valid < '%s' \
		GROUP by t.id, hour) as foo \
	GROUP by id" % (sts24h.strftime("%Y-%m-%d %H:%M"), \
		ets.strftime("%Y-%m-%d %H:%M") ) ).dictresult()
for i in range(len(rs)):
	pcpn[ rs[i]["station"] ] = "%5.2f" % (float(rs[i]["sum"]),)

pcpn["MXO"] = "M"

lows = {}
rs = iemaccess.query("SELECT t.id as station, \
	round(min(tmpf)::numeric,0) as min_tmpf, \
	count(tmpf) as obs FROM current_log c, stations t\
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid > '%s' and \
	valid < '%s' and tmpf > -99 GROUP by t,id" % \
        ( sts6z.strftime("%Y-%m-%d %H:%M"), ets.strftime("%Y-%m-%d %H:%M")) ).dictresult()

for i in range(len(rs)):
	lows[ rs[i]["station"] ] = int(rs[i]["min_tmpf"])




for s in st.ids:
	myP = "M"
	myH = "M"
	myL = "M"
	if pcpn.has_key(s):
		myP = pcpn[s]
	if lows.has_key(s):
		myL = lows[s]
	if highs.has_key(s):
		myH = highs[s]

	out.write( fmt % (s, st.sts[s]["name"], myH, \
		myL, \
		myP, "M", "M") )

out.write(".END\n")
out.close()

cmd = "/home/ldm/bin/pqinsert -p 'plot ac %s0000 awos_rtp_00z.shef awos_rtp_00z.shef shef' /tmp/awos_rtp.shef" % (ets.strftime("%Y%m%d"), )
os.system(cmd)
