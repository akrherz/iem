# Assign a site to each site in the mesosite database
# Daryl Herzmann 5 May 2004

from pyIEM import iemdb
i = iemdb.iemdb()
mydb = i['mesosite']

# Query out all sites with a null climate_site
rs = mydb.query("""SELECT id, geom, state from stations 
	WHERE climate_site IS NULL and country = 'US'
	""").dictresult()

for i in range(len(rs)):
	thisID = rs[i]["id"]
	thisGEOM = rs[i]["geom"]
	st = rs[i]['state']
	sql = """UPDATE stations SET climate_site = 
		(select id from stations WHERE network = '%sCLIMATE'
                 and substr(id,3,4) != '0000' and substr(id,3,1) != 'C'
		 ORDER by distance(geom, '%s') ASC LIMIT 1) WHERE 
			id = '%s' RETURNING climate_site""" % (st, thisGEOM, thisID)
	rs2 = mydb.query(sql).dictresult()
	print thisID, rs2[0]['climate_site']
