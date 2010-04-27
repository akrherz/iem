# Process CoCoRaHS Stations!

import urllib2, os, sys
from pyIEM import iemdb
i = iemdb.iemdb()
mesosite = i['mesosite']

state = sys.argv[1]

req = urllib2.Request("http://www.cocorahs.org/export/exportstations.aspx?State=%s&Format=CSV" % (state,) )
data = urllib2.urlopen(req).readlines()

# Find current stations
stations = []
sql = "SELECT id from stations WHERE network = '%sCOCORAHS'" % (state,)
rs = mesosite.query(sql).dictresult()
for i in range(len(rs)):
  stations.append( rs[i]['id'] )

# Process Header
header = {}
h = data[0].split(",")
for i in range(len( h )):
  header[ h[i] ] = i

for row in  data[1:]:
  cols = row.split(",")
  id = cols[ header["StationNumber"] ]
  if (id in stations):
    continue

  name = cols[ header["StationName"] ].strip().replace("'",' ')
  cnty = cols[ header["County"] ].strip().replace("'",' ')
  lat = cols[ header["Latitude"] ].strip()
  lon = cols[ header["Longitude"] ].strip()

  if (name == "" or lat == "" or lon == ""):
    continue

  print "NEW COCORAHS SITE", id, name, cnty
  
  sql = "INSERT into stations(id, synop, name, state, country, network, online,\
         geom, county, plot_name \
         ) VALUES ('%s',99999, '%s', '%s', 'US', '%sCOCORAHS', 't',\
         'SRID=4326;POINT(%s %s)', '%s', '%s')" % (id, name,\
         state, state, lon, lat, cnty, name)
  mesosite.query(sql)

  cmd = "/mesonet/scripts/iemaccess/addSiteMesosite.py %sCOCORAHS %s" % (state, id)
  os.system(cmd)
