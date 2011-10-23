
import urllib2, re, time
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

mcursor.execute("""
 SELECT network, x(geom) as lon, y(geom) as lat, elevation, id from stations 
 WHERE (elevation < -990 or elevation is null)""")

for row in mcursor:
  elev = row[3]
  lat = row[2]
  lon = row[1]
  id = row[4]
  network = row[0]
  r = urllib2.urlopen('http://weather.gladstonefamily.net/cgi-bin/wx-get-elevation.pl?lat=%s&lng=%s' % (lat,lon)).read()
  tokens =  re.findall(' ele="([0-9\.\-]*)" ', r)
  if len(tokens) == 0:
    print 'ERROR WITH ', id, r
    continue
  newelev = float(tokens[0])

  print "%7s %s OLD: %s NEW: %.3f" % (id, network, elev, newelev)
  mcursor2.execute("UPDATE stations SET elevation = %s WHERE id = '%s' and network = '%s'" % (newelev, id, network))
  time.sleep(2)

mcursor2.close()
MESOSITE.commit()
