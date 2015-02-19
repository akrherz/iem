'''
 We have a somewhat hack whereby we assign the proper sector to the climate
 site.  So a climate site like Ames gets assigned to the IAC005 (central Iowa)
'''

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

# Query out all sites with a null climate_site
mcursor.execute("""
  SELECT id, state from stations WHERE network ~* 'CLIMATE'
""")

for row in mcursor:
    sid = row[0]
    state = row[1]
    # Find the closest site
    mcursor2.execute("""
    select id from stations WHERE network = '%sCLIMATE'
    and substr(id,3,1) = 'C'
    ORDER by ST_distance(geom, (SELECT geom from stations WHERE
    id = '%s' and network = '%sCLIMATE')) ASC LIMIT 1""" % (state, sid, state))
    row2 = mcursor2.fetchone()
    if row2 is None:
        print 'Could not find Climate Site for: %s' % (sid,)
    else:
        mcursor2.execute("""UPDATE stations SET climate_site = '%s' WHERE
         id = '%s'""" % (row2[0], sid))
    print 'Set Climate: %s for ID: %s' % (row2[0], sid)

mcursor2.close()
MESOSITE.commit()
