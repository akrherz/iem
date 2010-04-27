# 		yearPrec.py
# Script that generates yearlyPrecip data
#
######################################################


from pyIEM import iemAccess, iemdb, stationTable
import mx.DateTime, string
iemaccess = iemAccess.iemAccess()
i = iemdb.iemdb()
st = stationTable.stationTable("/mesonet/TABLES/coop.stns")
mydb = i["coop"]
mesositedb = i["mesosite"]

o = open('IEMNWSYPR.txt','w')
o.write("IEMNWSYPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION YEAR PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER\n")

now = mx.DateTime.now()
goodDay = now.strftime("%Y-%m-%d")
jdays = now.strftime("%j")

# Now we load climatology
climo = {}
rs = mesositedb.query("SELECT id, climate_site from stations WHERE \
	network = 'IA_COOP'").dictresult()
for i in range(len(rs)):
	climo[ rs[i]["id"] ] = rs[i]["climate_site"]

mrain = {}
rs = mydb.query("select station, sum(precip) as rain from climate WHERE \
	valid <= '%s' \
	GROUP by station" % (now.strftime("2000-%m-%d"), ) ).dictresult()
for i in range(len(rs)):
	mrain[ string.upper(rs[i]["station"]) ] = rs[i]["rain"]


o.write("   TOTAL REPORTS POSSIBLE: %s\n" % (jdays) )

o.write("   VALID FOR YEAR THRU: "+ string.upper( now.strftime("%d %B %Y") ) +"\n\n")
o.write("%-6s%-24.24s%9s%10s%11s%10s\n" % ('ID', 'STATION', 'REPORTS', \
	'PREC (IN)', 'CLIMO2DATE', 'DIFF') )

queryStr = "SELECT station, count(station) as cnt, \
  sum(CASE WHEN pday > 0 THEN pday ELSE 0 END) as prectot from summary \
	WHERE extract(year from day) = %s and network = 'IA_COOP' and pday >= 0 \
  GROUP by station" % (now.year,)

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
