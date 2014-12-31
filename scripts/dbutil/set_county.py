"""
  Need to set station metadata for county name for a given site...
"""

import psycopg2
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
pcursor = POSTGIS.cursor()

pcursor.execute("""
  select s.id, c.name, s.iemid from stations s, ugcs c WHERE 
  ST_Contains(c.geom, s.geom) and s.geom && c.geom 
  and s.county IS NULL and s.state = substr(c.ugc,1,2) 
  and s.country = 'US' and c.end_ts is null and substr(c.ugc,3,1) = 'C'
""")

for row in pcursor:
    sid = row[0]
    cnty = row[1]
    iemid = row[2]
    print 'Assinging IEMID: %s SID: %s to county: %s' % (iemid, sid, cnty)
    mcursor2.execute("""UPDATE stations SET county = %s WHERE iemid = %s""", 
                     (cnty, iemid) )

pcursor.execute("""
  select s.id, c.ugc, s.iemid from stations s, ugcs c WHERE 
  ST_Contains(c.geom, s.geom) and s.geom && c.geom 
  and s.ugc_county IS NULL and s.state = substr(c.ugc,1,2) 
  and s.country = 'US' and substr(c.ugc,3,1) = 'C' 
  and c.end_ts is null LIMIT 1000
""")

for row in pcursor:
    sid = row[0]
    cnty = row[1]
    if cnty is None:
        continue
    iemid = row[2]
    print 'Assinging IEMID: %s SID: %s to ugc_county: %s' % (iemid, sid, cnty)
    mcursor2.execute("""UPDATE stations SET ugc_county = %s WHERE iemid = %s""", 
                     (cnty, iemid) )

pcursor.execute("""
  select s.id, c.ugc, s.iemid from stations s, ugcs c WHERE 
  ST_Contains(c.geom, s.geom) and s.geom && c.geom 
  and s.ugc_zone IS NULL and s.state = substr(c.ugc,1,2) 
  and s.country = 'US' and substr(c.ugc,3,1) = 'Z' and
  c.end_ts is null LIMIT 1000
""")

for row in pcursor:
    sid = row[0]
    cnty = row[1]
    if cnty is None:
        continue
    iemid = row[2]
    print 'Assinging IEMID: %s SID: %s to ugc_zone: %s' % (iemid, sid, cnty)
    mcursor2.execute("""UPDATE stations SET ugc_zone = %s WHERE iemid = %s""", 
                     (cnty, iemid) )

mcursor2.close()
MESOSITE.commit()
