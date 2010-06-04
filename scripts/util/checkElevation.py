
import urllib2, re
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

rs = mesosite.query("SELECT network, x(geom) as lon, y(geom) as lat, elevation, id from stations WHERE elevation = 342").dictresult()

for i in range(len(rs)):
  elev = rs[i]['elevation']
  lat = rs[i]['lat']
  lon = rs[i]['lon']
  id = rs[i]['id']
  network = rs[i]['network']
  r = urllib2.urlopen('http://www.earthtools.org/height/%s/%s' % (lat,lon)).read()
  newelev =  re.findall("<meters>(.*)</meters>", r)[0]

  print id, elev, newelev
  mesosite.query("UPDATE stations SET elevation = %s WHERE id = '%s' and network = '%s'" % (newelev, id, network))
   
