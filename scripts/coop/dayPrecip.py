######################################################

from pyIEM import iemAccess, iemdb, stationTable
import mx.DateTime, string
iemaccess = iemAccess.iemAccess()
i = iemdb.iemdb()
st = stationTable.stationTable("/mesonet/TABLES/coop.stns")
mydb = i["coop"]
mesositedb = i["mesosite"]

o = open('IEMNWSDPR.txt','w')
o.write("IEMNWSDPR\n")
o.write("IOWA ENVIRONMENTAL MESONET\n")
o.write("   NWS COOP STATION DAY PRECIPITATION TOTALS\n")
o.write("   AS CALCULATED ON THE IEM SERVER\n")

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
rs = mydb.query("select station, precip as rain from climate WHERE \
	valid = '%s' " % (now.strftime("2000-%m-%d"), ) ).dictresult()
for i in range(len(rs)):
	mrain[ string.upper(rs[i]["station"]) ] = rs[i]["rain"]


o.write("   VALID AT 7AM ON: "+ string.upper( now.strftime("%d %b %Y") ) +"\n\n")
o.write("%-6s%-24s%10s%11s%10s\n" % ('ID', 'STATION', \
	'PREC (IN)', 'CLIMO4DATE', 'DIFF') )

queryStr = "SELECT station,  pday  as prectot from summary \
	WHERE day = '%s' and network = 'IA_COOP' and pday >= 0" % (now.strftime("%Y-%m-%d"),)

rs = iemaccess.query(queryStr).dictresult()

d = {}
for i in range(len(rs)):
	thisStation = rs[i]["station"]
	thisPrec = rs[i]["prectot"]
	if (st.sts.has_key(thisStation)):
		d[thisStation] = {'prectot': float(rs[i]["prectot"]) }
		d[thisStation]["name"] = st.sts[thisStation]['name']
		d[thisStation]["crain"] = mrain[ climo[thisStation] ]

keys = d.keys()
keys.sort()

for k in keys:
	o.write("%-6s%-24.24s%10.2f%11.2f%10.2f\n" % ( k, d[k]["name"], \
		d[k]["prectot"], d[k]["crain"], \
		d[k]["prectot"] - d[k]["crain"] ) )


o.write(".END\n")
o.close()
