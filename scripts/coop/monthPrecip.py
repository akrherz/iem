# 		monthPrec.py
# Script that generates monthlyPrecip data
#
# Daryl Herzmann 25 SEP 2001
# 27 Jan 2002:	Actually use t2002
# 07 Feb 2002:	Make sure that Precip >= 0
# 28 Aug 2002:	COOP database has moved to DB1
# 16 Jan 2003:	Not sure if this is used, but lets update anyway
# 21 Sep 2003	Stupid thing!, Augh...
# 28 May 2004	Add in climo support
# 23 Jul 2004	Use IEM Access for goodness sakes!
#####################################################

from pyIEM import iemAccess, iemdb, stationTable
import  mx.DateTime, string
iemaccess = iemAccess.iemAccess()
i = iemdb.iemdb()
st = stationTable.stationTable("/mesonet/TABLES/coop.stns")
mydb = i['coop']
mesositedb =  i["mesosite"]

o = open('IEMNWSMPR.txt','w')
o.write("IEMNWSMPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION MONTH PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER ...NOTE THE OBS COUNT...\n")

now = mx.DateTime.now() 
goodDay = now.strftime("%Y-%m-%d")

# Now we load climatology
climo = {}
rs = mesositedb.query("SELECT id, climate_site from stations WHERE \
	network = 'IA_COOP'").dictresult()
for i in range(len(rs)):
	climo[ rs[i]["id"] ] = rs[i]["climate_site"]

# Now we load climatology
mrain = {}
rs = mydb.query("select station, sum(precip) as rain from climate WHERE \
	extract(month from valid) = %s and extract(day from valid) <= %s \
	GROUP by station" % (now.month, now.day) ).dictresult()
for i in range(len(rs)):
	mrain[ string.upper(rs[i]["station"]) ] = rs[i]["rain"]


o.write("   VALID FOR MONTH OF: "+ string.upper( now.strftime("%d %b %Y") ) +"\n\n")
o.write("%-6s%-24.24s%9s%10s%11s%10s\n" % ('ID', 'STATION', 'REPORTS',\
	'PREC (IN)', 'CLIMO2DATE', 'DIFF') )

queryStr = "SELECT station, count(station) as cnt, \
	sum(CASE WHEN pday >= 0 THEN pday ELSE 0 END) as prectot from summary \
	WHERE date_part('month', day) = date_part('month', CURRENT_TIMESTAMP::date)\
	and pday >= 0 and network = 'IA_COOP' and \
	extract(year from day) = %s GROUP by station" % (now.year,)

rs = iemaccess.query(queryStr).dictresult()

d = {}
for i in range(len(rs)):
	thisStation = rs[i]["station"]
	thisPrec = rs[i]["prectot"]
	thisCount = rs[i]["cnt"]
	if (st.sts.has_key(thisStation)):
		d[thisStation] = {'prectot': float(rs[i]["prectot"]),
						 'cnt': float(rs[i]['cnt']) }
		d[thisStation]["name"] = st.sts[thisStation]['name']
		d[thisStation]["crain"] = mrain[ climo[thisStation] ]

keys = d.keys()
keys.sort()

for k in keys:
	o.write("%-6s%-24.24s%9.0f%10.2f%11.2f%10.2f\n" % ( k, d[k]["name"], \
		d[k]["cnt"], d[k]["prectot"], d[k]["crain"], \
		d[k]["prectot"] - d[k]["crain"] ) )


o.write(".END\n")
o.close()
