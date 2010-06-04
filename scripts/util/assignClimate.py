# Assign a COOPDB site to each site in the mesosite database
# Daryl Herzmann 5 May 2004

from pyIEM import iemdb
i = iemdb.iemdb()
mydb = i['mesosite']

# Query out all sites with a null climate_site
rs = mydb.query("SELECT id, geom from stations \
	WHERE climate_site IS NULL and state = 'IA'").dictresult()

for i in range(len(rs)):
	print rs[i]
	thisID = rs[i]["id"]
	thisGEOM = rs[i]["geom"]
	sql = "UPDATE stations SET climate_site = \
		(select id from stations WHERE network = 'IACLIMATE' \
		 ORDER by distance(geom, '%s') ASC LIMIT 1) WHERE \
			id = '%s' " % (thisGEOM, thisID)
	mydb.query(sql)
