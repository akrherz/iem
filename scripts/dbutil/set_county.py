"""
  Need to set station metadata for county name for a given site...
"""

import re
import iemdb
MESOSITE = iemdb.connect('mesosite')
POSTGIS = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
pcursor = POSTGIS.cursor()

mcursor.execute("""
  select s.id, c.name from stations s, counties c, states t WHERE 
  ST_Contains(c.the_geom, s.geom) and s.geom && c.the_geom 
  and s.county IS NULL and s.state = t.state_abbr and
  t.state_fips = c.state_fips and s.country = 'US'
""")

for row in mcursor:
    sid = row[0]
    cnty = re.sub("'", " ", row[1])
    print 'Assinging ID: %s to county: %s' % (sid, cnty)
    mcursor2.execute("""UPDATE stations SET county = %s WHERE id = %s""", 
                     (cnty, sid) )

pcursor.execute("""
  select s.id, c.ugc, s.iemid from stations s, nws_ugc c WHERE 
  ST_Contains(c.the_geom, s.geom) and s.geom && c.the_geom 
  and s.ugc_county IS NULL and s.state = substr(c.state,1,2) 
  and s.country = 'US' and c.polygon_class = 'C' LIMIT 1000
""")

for row in mcursor:
    sid = row[2]
    cnty = row[1]
    print 'Assinging ID: %s to ugc_county: %s' % (sid, cnty)
    mcursor2.execute("""UPDATE stations SET ugc_county = %s WHERE iemid = %s""", 
                     (cnty, sid) )

pcursor.execute("""
  select s.id, c.ugc, s.iemid from stations s, nws_ugc c WHERE 
  ST_Contains(c.the_geom, s.geom) and s.geom && c.the_geom 
  and s.ugc_county IS NULL and s.state = substr(c.state,1,2) 
  and s.country = 'US' and c.polygon_class = 'Z' LIMIT 1000
""")

for row in mcursor:
    sid = row[2]
    cnty = row[1]
    print 'Assinging ID: %s to ugc_zone: %s' % (sid, cnty)
    mcursor2.execute("""UPDATE stations SET ugc_zone = %s WHERE iemid = %s""", 
                     (cnty, sid) )

mcursor2.close()
MESOSITE.commit()
