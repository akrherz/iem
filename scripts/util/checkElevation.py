
import urllib2, re, time
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

rs = mesosite.query("""
 SELECT network, x(geom) as lon, y(geom) as lat, elevation, id from stations 
 WHERE (elevation = 0 or elevation is null) LIMIT 1000""").dictresult()

for i in range(len(rs)):
  elev = rs[i]['elevation']
  lat = rs[i]['lat']
  lon = rs[i]['lon']
  id = rs[i]['id']
  network = rs[i]['network']
  #r = urllib2.urlopen('http://www.earthtools.org/height/%s/%s' % (lat,lon)).read()
  #newelev =  re.findall("<meters>(.*)</meters>", r)[0]
  r = urllib2.urlopen('http://weather.gladstonefamily.net/cgi-bin/wx-get-elevation.pl?lat=%s&lng=%s' % (lat,lon)).read()
  print r
  tokens =  re.findall(' ele="([0-9\.\-]*)" ', r)
  if len(tokens) == 0:
    print 'ERROR WITH ', id
    continue
  newelev = float(tokens[0])

  print "%7s %s OLD: %s NEW: %.3f" % (id, network, elev, newelev)
  mesosite.query("UPDATE stations SET elevation = %s WHERE id = '%s' and network = '%s'" % (newelev, id, network))
  time.sleep(2)
