"""
Yearly precip something
"""
import network
nt = network.Table("IA_COOP")
import  mx.DateTime
import iemdb
import subprocess
import os
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

o = open('IEMNWSYPR.txt','w')
o.write("IEMNWSYPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION YEAR PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER\n")

now = mx.DateTime.now()
goodDay = now.strftime("%Y-%m-%d")
jdays = now.strftime("%j")

mrain = {}
ccursor.execute("""select station, sum(precip) as rain from climate WHERE 
	valid <= '%s' 
	GROUP by station""" % (now.strftime("2000-%m-%d"), ) )
for row in ccursor:
	mrain[ row[0] ] = row[1]


o.write("   TOTAL REPORTS POSSIBLE: %s\n" % (jdays) )

o.write("   VALID FOR YEAR THRU: %s\n\n" % (now.strftime("%d %B %Y"),)) 
o.write("%-6s%-24.24s%9s%10s%11s%10s\n" % ('ID', 'STATION', 'REPORTS', 
	'PREC (IN)', 'CLIMO2DATE', 'DIFF') )

queryStr = """SELECT id, count(id) as cnt, 
  sum(CASE WHEN pday > 0 THEN pday ELSE 0 END) as prectot 
  from summary_%s s JOIN stations t ON (s.iemid = t.iemid) 
	WHERE t.network = 'IA_COOP' and pday >= 0 
  GROUP by id""" % (now.year, )

icursor.execute( queryStr )

d = {}
for row in icursor:
	thisStation = row[0]
	thisPrec = row[2]
	thisCount = row[1]
	if nt.sts.has_key(thisStation):
		d[thisStation] = {'prectot': thisCount,
						 'cnt': thisPrec }
		d[thisStation]["name"] = nt.sts[thisStation]['name']
		d[thisStation]["crain"] = mrain[ nt.sts[thisStation]['climate_site'] ]

keys = d.keys()
keys.sort()

for k in keys:
	o.write("%-6s%-24.24s%9.0f%10.2f%11.2f%10.2f\n" % ( k, d[k]["name"], 
		d[k]["cnt"], d[k]["prectot"], d[k]["crain"], 
		d[k]["prectot"] - d[k]["crain"] ) )


o.write(".END\n")
o.close()

subprocess.call("/home/ldm/bin/pqinsert -p 'plot c 000000000000 text/IEMNWSYPR.txt bogus txt' IEMNWSYPR.txt",
	shell=True)

os.unlink("IEMNWSYPR.txt")