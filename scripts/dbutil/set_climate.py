# Assign a site to each site in the mesosite database
# Daryl Herzmann 5 May 2004

import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Query out all sites with a null climate_site
mcursor.execute("""SELECT id, geom, state from stations 
	WHERE climate_site IS NULL and country = 'US' and state != 'PR'
	""")

for row in mcursor:
	thisID = row[0]
	thisGEOM = row[1]
	st = row[2]
        # Find the closest site
	sql = """select id from stations WHERE network = '%sCLIMATE'
                 and substr(id,3,4) != '0000' and substr(id,3,1) != 'C'
		 ORDER by distance(geom, '%s') ASC LIMIT 1""" % (
                   st, thisGEOM)
	mcursor2.execute(sql)
        row = mcursor2.fetchone()
        if row is None:
            print 'Could not find Climate Site for: %s' % (thisID,)
        else:
	    sql = """UPDATE stations SET climate_site = '%s' WHERE
             id = '%s'""" % (row[0], thisID)
            mcursor2.execute(sql)
            print 'Set Climate: %s for ID: %s' % (row[0], thisID)

mcursor2.close()
MESOSITE.commit()
