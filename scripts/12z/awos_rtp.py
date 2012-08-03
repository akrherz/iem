"""
 Andy Ervin wants something to extract 12z 12 hr hi/lo values
 12 May 2004
"""

import mx.DateTime
import subprocess
import network
nt = network.Table("AWOS")
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()


ets = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hour=12,minute=0)
sts = ets + mx.DateTime.RelativeDateTime(days=-1)

#CWI   :CLINTON ARPT       :  79 /  64 /     M /    M /  M
fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

out = open("/tmp/awos_rtp.shef", 'w')
out.write("""


.BR DMX %s Z DH06/TAIRZX/DH12/TAIRZP/PP/SF/SD
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   HIGH TEMPERATURE FOR %s
:   00Z TO 12Z TODAY LOW TEMPERATURE
:   12Z YESTERDAY TO 12Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
""" % ( ets.strftime("%m%d"), sts.strftime("%d %b %Y").upper() ) )

highs = {}
icursor.execute("""SELECT id, 
	round(max(tmpf)::numeric,0) as max_tmpf, 
	count(tmpf) as obs FROM current_log c, stations t 
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and date(valid) = '%s' 
	and tmpf > -99 GROUP by id """ % (sts.strftime("%Y-%m-%d %H:%M"),) )

for row in icursor:
	highs[ row[0] ] = row[1]

icursor.execute("SET TIME ZONE 'GMT'")

# 12z to 12z precip
pcpn = {}
icursor.execute("""select id, sum(precip) from 
		(select id, extract(hour from valid) as hour, 
		max(phour) as precip from current_log c, stations t 
		WHERE t.network = 'AWOS' and t.iemid = c.iemid 
		and valid  >= '%s' and valid < '%s' 
		GROUP by id, hour) as foo 
	GROUP by id""" % (sts.strftime("%Y-%m-%d %H:%M"), 
		ets.strftime("%Y-%m-%d %H:%M") ) )
for row in icursor:
	pcpn[ row[0] ] = "%5.2f" % (row[1],)

#pcpn["DEH"] = "M"
#pcpn["VTI"] = "M"
#pcpn["IIB"] = "M"
#pcpn["PEA"] = "M"
#pcpn["MXO"] = "M"
#pcpn["MPZ"] = "M"

lows = {}
icursor.execute("""SELECT id, 
	round(min(tmpf)::numeric,0) as min_tmpf, 
	count(tmpf) as obs FROM current_log c, stations t 
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and date(valid) = 'TODAY' and 
	extract(hour from valid) < 12 and tmpf > -99 GROUP by id""")

for row in icursor:
	lows[ row[0] ] = row[1]


for s in nt.sts.keys():
	myP = "M"
	myH = "M"
	myL = "M"
	if pcpn.has_key(s):
		myP = pcpn[s]
	if lows.has_key(s):
		myL = lows[s]
	if highs.has_key(s):
		myH = highs[s]

	out.write( fmt % (s, nt.sts[s]["name"], myH, 
		myL, 
		myP, "M", "M") )

out.write(".END\n")
out.close()

cmd = "/home/ldm/bin/pqinsert -p 'plot ac %s0000 awos_rtp.shef awos_rtp.shef shef' /tmp/awos_rtp.shef" % (ets.strftime("%Y%m%d"), )
subprocess.call(cmd, shell=True)
