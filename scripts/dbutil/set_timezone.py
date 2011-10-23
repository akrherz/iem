"""
Need something to set the time zone of sites, finally
"""
import iemdb
MESOSITE = iemdb.connect('mesosite')
POSTGIS = iemdb.connect('postgis')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()
pcursor = POSTGIS.cursor()

mcursor.execute("""
 SELECT id, network, x(geom) as lon, y(geom) as lat from stations 
 WHERE tzname is null""")

for row in mcursor:
  lat = row[3]
  lon = row[2]
  id = row[0]
  network = row[1]

  pcursor.execute("""
select tzid from tz where ST_Contains(the_geom, 'SRID=4326;POINT(%s %s)');
  """ % (lon, lat))
  row2 = pcursor.fetchone()
  if row2 == None or row2[0] == 'uninhabited':
    print '--> MISSING ID: %s NETWORK: %s LAT: %.2f LON: %.2f' % (id, 
     network, lat, lon)
    
    mcursor2.execute("""SELECT ST_Distance(geom, 'SRID=4326;POINT(%s %s)') as d, id, tzname from stations WHERE network = '%s' and tzname is not null ORDER by d ASC LIMIT 1""" % (lon, lat, network))
    row3 = mcursor2.fetchone()
    if row3 is not None:
      print 'FORCING DCP to its neighbor: %s Tzname: %s Distance: %.5f' % (
          row3[1], row3[2], row3[0])
      mcursor2.execute("UPDATE stations SET tzname = '%s' WHERE id = '%s' and network = '%s'" % (row3[2], id, network))
    else:
      print 'BAD, CAN NOT FORCE EVEN!'
  else:
    print 'ID: %s NETWORK: %s TIMEZONE: %s' % (id, network, row2[0])
    mcursor2.execute("UPDATE stations SET tzname = '%s' WHERE id = '%s' and network = '%s'" % (row2[0], id, network))

mcursor2.close()
MESOSITE.commit()
