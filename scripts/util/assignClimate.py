# Assign a COOPDB site to each site in the mesosite database
# Daryl Herzmann 5 May 2004

from pyIEM import iemdb
i = iemdb.iemdb()
mydb = i['mesosite']

# Query out all sites with a null climate_site
rs = mydb.query("""SELECT id, geom, state from stations 
	WHERE climate_site IS NULL""").dictresult()

for i in range(len(rs)):
	print rs[i]
	thisID = rs[i]["id"]
	thisGEOM = rs[i]["geom"]
	st = rs[i]['state']
	sql = """UPDATE stations SET climate_site = 
		(select id from stations WHERE network = '%sCLIMATE' 
		 ORDER by distance(geom, '%s') ASC LIMIT 1) WHERE 
			id = '%s' """ % (st, thisGEOM, thisID)
	mydb.query(sql)
