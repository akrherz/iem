
import csv, os
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

stations = {}
rs = mesosite.query("SELECT * from stations WHERE network = 'SD_RWIS'").dictresult()
for i in range(len(rs)):
  stations[ rs[i]['id'] ] = 1

names = {}
r = csv.DictReader( open('clarus-site.csv') )
for row in r:
  if (row['contribId'] != '44'):
    continue
  sid = row['id']
  names[sid] = row['description']

r = csv.DictReader( open('clarus.csv') )

for row in r:
  if (row['contribId'] != '44'):
    continue

  sid = row['siteId']
  sname = names[sid].replace("'", "")
  station = "CL%s" % ( sid,)
  if (stations.has_key(station)):
    continue
  lat = row['locBaseLat']
  lon = row['locBaseLong']
  elev = row['locBaseElev']

  print "adding [%s] %s" % (station, sname)
  sql = "INSERT into stations (id, network) values ('%s','%s_RWIS')" % (station, 'SD')
  mesosite.query(sql)

  sql = "UPDATE stations SET synop = 9999, country = 'US', plot_name = '%s', name = '%s', state = '%s', elevation = %s, online = 't', geom = 'SRID=4326;POINT(%s %s)', latitude = %s, longitude = %s WHERE id = '%s' and network = '%s_RWIS' " % (sname[:39], sname[:39], 'SD', elev, lon, lat, lat, lon, station, 'SD')
  mesosite.query(sql)

  cmd = "/mesonet/scripts/iemaccess/addSiteMesosite.py %s_RWIS %s" % ('SD', station)
  os.system(cmd)

