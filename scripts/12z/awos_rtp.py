# Andy Ervin wants something to extract 12z 12 hr hi/lo values
# Daryl Herzmann 12 May 2004

from pyIEM import iemAccess, stationTable
iemaccess = iemAccess.iemAccess()
import mx.DateTime, shutil, string, os
st = stationTable.stationTable("/mesonet/TABLES/awos.stns")


ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=12,minute=0)
sts = ets + mx.DateTime.RelativeDateTime(days=-1)

#CWI   :CLINTON ARPT       :  79 /  64 /     M /    M /  M
fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

out = open("/tmp/awos_rtp.shef", 'w')
out.write("""


.BR DSM %s Z DH06/TAIRZX/DH12/TAIRZP/PPDRZZ/SFDRZZ/SDIRZZ
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   HIGH TEMPERATURE FOR %s
:   00Z TO 12Z TODAY LOW TEMPERATURE
:   12Z YESTERDAY TO 12Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
""" % ( ets.strftime("%m%d"), string.upper(sts.strftime("%d %b %Y")) ) )

highs = {}
rs = iemaccess.query("SELECT station, \
	round(max(tmpf)::numeric,0) as max_tmpf, \
	count(tmpf) as obs FROM current_log \
	WHERE network = 'AWOS' and date(valid) = '%s' \
	and tmpf > -99 GROUP by station " % \
	(sts.strftime("%Y-%m-%d %H:%M"),) ).dictresult()

for i in range(len(rs)):
	highs[ rs[i]["station"] ] = int(rs[i]["max_tmpf"])

iemaccess.query("SET TIME ZONE 'GMT'")

# 12z to 12z precip
pcpn = {}
rs = iemaccess.query("select station, sum(precip) from \
		(select station, extract(hour from valid) as hour, \
		max(phour) as precip from current_log WHERE network = 'AWOS' \
		and valid  >= '%s' and valid < '%s' \
		GROUP by station, hour) as foo \
	GROUP by station" % (sts.strftime("%Y-%m-%d %H:%M"), \
		ets.strftime("%Y-%m-%d %H:%M") ) ).dictresult()
for i in range(len(rs)):
	pcpn[ rs[i]["station"] ] = "%5.2f" % (float(rs[i]["sum"]),)

#pcpn["DEH"] = "M"
#pcpn["VTI"] = "M"
#pcpn["IIB"] = "M"
#pcpn["PEA"] = "M"
#pcpn["MXO"] = "M"
#pcpn["MPZ"] = "M"

lows = {}
rs = iemaccess.query("SELECT station, \
	round(min(tmpf)::numeric,0) as min_tmpf, \
	count(tmpf) as obs FROM current_log \
	WHERE network = 'AWOS' and date(valid) = 'TODAY' and \
	extract(hour from valid) < 12 and tmpf > -99 GROUP by station").dictresult()

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

cmd = "/home/ldm/bin/pqinsert -p 'plot ac %s0000 awos_rtp.shef awos_rtp.shef shef' /tmp/awos_rtp.shef" % (ets.strftime("%Y%m%d"), )
os.system(cmd)
