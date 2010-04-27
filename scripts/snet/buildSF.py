#!/mesonet/python/bin/python
# Need something to build a GEMPAK surface file 
# Daryl Herzmann 22 Mar 2004
# 23 Mar 2004	Augh, use GMT!
# 31 Mar 2004	Caught error when this bad boy runs at 12:03 AM

from pyIEM import iemAccessDatabase
iemdb = iemAccessDatabase.iemAccessDatabase()
import mx.DateTime

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minutes=-3)
sftime = now.strftime("%y%m%d/%H%M")

def main():
	rs = iemdb.query("SELECT *, s.pmonth from current c, summary s \
		WHERE s.day = 'TODAY' and s.station = c.station and \
		c.network IN ('KCCI', 'KELO') and \
		c.valid > (CURRENT_TIMESTAMP - '40 minutes'::interval)").dictresult()

	out = open("sfedit.fil", 'w')
	for i in range(len(rs)):
		rs[i]["smph"] = rs[i]["sknt"] * 1.15
		try:
			out.write("%7s %s %4i %4i %4i %4i %4.1f %4.2f %4i %4.2f %4.2f %3i\n" %\
		(rs[i]["station"], sftime, rs[i]["tmpf"], rs[i]["relh"], rs[i]["dwpf"],\
		rs[i]["drct"], rs[i]["smph"], rs[i]["pday"], rs[i]["srad"], \
		rs[i]["pres"], rs[i]["pmonth"], rs[i]["max_gust"]) )
		except TypeError:
			continue

	out.close()



main()
