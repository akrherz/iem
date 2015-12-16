"""
Daily precip something
"""
from pyiem.network import Table as NetworkTable
nt = NetworkTable("IA_COOP")
import datetime
import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
ccursor = COOP.cursor()

o = open('IEMNWSDPR.txt','w')
o.write("IEMNWSDPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION DAY PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER\n")

now = datetime.datetime.now() 
goodDay = now.strftime("%Y-%m-%d")

# Now we load climatology
mrain = {}
ccursor.execute("""select station, precip as rain from climate WHERE 
	valid = '%s' """ % (now.strftime("2000-%m-%d"), ) )
for row in ccursor:
	mrain[ row[0] ] = row[1]


o.write("   VALID AT 7AM ON: %s\n\n" % (now.strftime("%d %b %Y").upper(),))
o.write("%-6s%-24s%10s%11s%10s\n" % ('ID', 'STATION', 
	'PREC (IN)', 'CLIMO4DATE', 'DIFF') )

queryStr = """SELECT id,  pday  as prectot from summary_%s s 
	JOIN stations t ON (t.iemid = s.iemid) 
	WHERE day = '%s' and t.network = 'IA_COOP' and pday >= 0""" % (
							now.year, now.strftime("%Y-%m-%d"),)

icursor.execute(queryStr)

d = {}
for row in icursor:
	thisStation = row[0]
	thisPrec = row[1]
	if nt.sts.has_key(thisStation):
		d[thisStation] = {'prectot': thisPrec }
		d[thisStation]["name"] = nt.sts[thisStation]['name']
		d[thisStation]["crain"] = mrain[ nt.sts[thisStation]['climate_site'] ]

keys = d.keys()
keys.sort()

for k in keys:
	o.write("%-6s%-24.24s%10.2f%11.2f%10.2f\n" % ( k, d[k]["name"], 
		d[k]["prectot"], d[k]["crain"], 
		d[k]["prectot"] - d[k]["crain"] ) )


o.write(".END\n")
o.close()
