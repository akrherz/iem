"""
 Assign a climate site to each site in the mesosite database, within reason
"""

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

def do(col):
	# Query out all sites with a null climate_site
	mcursor.execute("""
		SELECT id, geom, state from stations 
		WHERE """+col+""" IS NULL and country = 'US' and 
		state not in ('PR','DC','GU','PU','P3', 'P4')
	""")
	
	for row in mcursor:
		thisID = row[0]
		thisGEOM = row[1]
		st = row[2]
		# Find the closest site
		if col == 'climate_site':
			sql = """select id from stations WHERE network = '%sCLIMATE'
	                 and substr(id,3,4) != '0000' and substr(id,3,1) != 'C'
			 ORDER by ST_distance(geom, '%s') ASC LIMIT 1""" % (
	                   st, thisGEOM)
		else:
			sql = """select id from stations WHERE network = 'NCDC81'
			 	ORDER by ST_distance(geom, '%s') ASC LIMIT 1""" % (thisGEOM,)
		mcursor2.execute(sql)
		row2 = mcursor2.fetchone()
		if row2 is None:
			print 'Could not find %s Site for: %s' % (col, thisID)
		else:
			sql = """UPDATE stations SET %s = '%s' WHERE
	             id = '%s'""" % (col, row2[0], thisID)
			mcursor2.execute(sql)
			print 'Set %s: %s for ID: %s' % (col, row2[0], thisID)

do("climate_site")
do("ncdc81")

mcursor2.close()
MESOSITE.commit()
