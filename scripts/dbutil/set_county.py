"""
  Need to set station metadata for county name for a given site...
$Id: $:
"""

import re
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

mcursor.execute("""
  select s.id, c.name from stations s, counties c, states t WHERE 
  ST_Contains(c.the_geom, s.geom) and s.geom && c.the_geom 
  and s.county IS NULL and s.state = t.state_abbr and
  t.state_fips = c.state_fips and s.country = 'US'
""")

for row in mcursor:
  id = row[0]
  cnty = re.sub("'", " ", row[1])
  print 'Assinging ID: %s to county: %s' % (id, cnty)
  mcursor2.execute("UPDATE stations SET county = '%s' WHERE id = '%s'" % (cnty, id) )

mcursor2.close()
MESOSITE.commit()
