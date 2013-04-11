"""
"""

import datetime
import pytz
import subprocess
import network
nt = network.Table("AWOS")
import iemdb
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

# We run at 12z 
now12z = datetime.datetime.utcnow()
now12z = now12z.replace(hour=12, minute=0, second=0, microsecond=0,
					tzinfo=pytz.timezone("UTC"))
today6z = now12z.replace(hour=6)
today0z = now12z.replace(hour=0)
yesterday6z = today6z - datetime.timedelta(days=1)
yesterday12z = now12z - datetime.timedelta(days=1)

fmt = "%-6s:%-19s: %3s / %3s / %5s / %4s / %2s\n"

out = open("/tmp/awos_rtp.shef", 'w')
out.write("""


.BR DMX %s Z DH06/TAIRZX/DH12/TAIRZP/PP/SF/SD
: IOWA AWOS RTP FIRST GUESS PROCESSED BY THE IEM
:   06Z to 06Z HIGH TEMPERATURE FOR %s
:   00Z TO 12Z TODAY LOW TEMPERATURE
:   12Z YESTERDAY TO 12Z TODAY RAINFALL
:   ...BASED ON REPORTED OBS...
""" % ( now12z.strftime("%m%d"), yesterday6z.strftime("%d %b %Y").upper() ) )

# 6z to 6z high temperature
highs = {}
sql = """SELECT id, 
	round(max(tmpf)::numeric,0) as max_tmpf, 
	count(tmpf) as obs FROM current_log c, stations t 
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid >= %s
	and valid < %s 
	and tmpf > -99 GROUP by id """
args = (yesterday6z, today6z) 
icursor.execute(sql, args)
for row in icursor:
	highs[ row[0] ] = row[1]

# 12z to 12z precip
pcpn = {}
sql = """select id, sum(precip) from 
		(select id, extract(hour from valid) as hour, 
		max(phour) as precip from current_log c, stations t 
		WHERE t.network = 'AWOS' and t.iemid = c.iemid 
		and valid  >= %s and valid < %s 
		GROUP by id, hour) as foo 
	GROUP by id"""
args = (yesterday12z, now12z)
icursor.execute(sql, args)
for row in icursor:
	pcpn[ row[0] ] = "%5.2f" % (row[1],)

# 0z to 12z
lows = {}
sql = """SELECT id, 
	round(min(tmpf)::numeric,0) as min_tmpf, 
	count(tmpf) as obs FROM current_log c, stations t 
	WHERE t.iemid = c.iemid and t.network = 'AWOS' and valid >= %s
	and valid < %s and 
	extract(hour from valid) < 12 and tmpf > -99 GROUP by id"""
args = (today0z, now12z)
icursor.execute(sql, args)
for row in icursor:
	lows[ row[0] ] = row[1]

ids = nt.sts.keys()
ids.sort()
for s in ids:
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

cmd = "/home/ldm/bin/pqinsert -p 'plot ac %s0000 awos_rtp.shef awos_rtp.shef shef' /tmp/awos_rtp.shef" % (now12z.strftime("%Y%m%d"), )
subprocess.call(cmd, shell=True)
