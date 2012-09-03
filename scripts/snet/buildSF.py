"""
 Need something to build a GEMPAK surface file 
 Daryl Herzmann 22 Mar 2004
 23 Mar 2004	Augh, use GMT!
 31 Mar 2004	Caught error when this bad boy runs at 12:03 AM
"""
import iemdb
IEM = iemdb.connect('iem', bypass=True)
import psycopg2.extras
icursor = IEM.cursor(cursor_factory=psycopg2.extras.DictCursor)
import mx.DateTime

now = mx.DateTime.gmt() + mx.DateTime.RelativeDateTime(minutes=-3)
sftime = now.strftime("%y%m%d/%H%M")

def main():
	icursor.execute("""SELECT *, s.pmonth from current c, summary_%s s, stations t 
		WHERE s.day = 'TODAY' and s.iemid = c.iemid and t.iemid = c.iemid and 
		t.network IN ('KCCI', 'KELO') and 
		c.valid > (CURRENT_TIMESTAMP - '40 minutes'::interval)""" % (
													now.year,) )

	out = open("sfedit.fil", 'w')
	for row in icursor:
		row2 = row.copy()
		row2["smph"] = row2["sknt"] * 1.15
		try:
			out.write("%7s %s %4i %4i %4i %4i %4.1f %4.2f %4i %4.2f %4.2f %3i\n" % (
		row2["id"], sftime, row2["tmpf"], row2["relh"], row2["dwpf"],
		row2["drct"], row2["smph"], row2["pday"], row2["srad"], 
		row2["pres"], row2["pmonth"], row2["max_gust"]) )
		except TypeError:
			continue

	out.close()



main()
