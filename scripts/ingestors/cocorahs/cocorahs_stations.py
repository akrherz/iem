# Process CoCoRaHS Stations!

import urllib2, os, sys
import iemdb
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

state = sys.argv[1]

req = urllib2.Request("http://data.cocorahs.org/cocorahs/export/exportstations.aspx?State=%s&Format=CSV" % (state,) )
data = urllib2.urlopen(req).readlines()

# Find current stations
stations = []
sql = "SELECT id from stations WHERE network = '%sCOCORAHS' and y(geom) > 0" % (state,)
mcursor.execute( sql )
for row in mcursor:
    stations.append( row[0] )

# Process Header
header = {}
h = data[0].split(",")
for i in range(len( h )):
    header[ h[i] ] = i

if not header.has_key('StationNumber'):
    sys.exit(0)

for row in  data[1:]:
  cols = row.split(", ")
  id = cols[ header["StationNumber"] ]
  if (id in stations):
    continue

  name = cols[ header["StationName"] ].strip().replace("'",' ')
  cnty = cols[ header["County"] ].strip().replace("'",' ')
  lat = cols[ header["Latitude"] ].strip()
  lon = cols[ header["Longitude"] ].strip()

  if (lat == "0" or lon == "-0"):
    continue

  print "NEW COCORAHS SITE", id, name, cnty, lat, lon
  
  sql = """INSERT into stations(id, synop, name, state, country, network, online,
         geom, county, plot_name , metasite
         ) VALUES ('%s',99999, '%s', '%s', 'US', '%sCOCORAHS', 't',
         'SRID=4326;POINT(%s %s)', '%s', '%s', 'f')""" % (id, name,
         state, state, lon, lat, cnty, name)
  try:
    mcursor.execute(sql)
  except:
    sql = """UPDATE stations SET geom = 'SRID=4326;POINT(%s %s)'
           WHERE id = '%s' and network = '%sCOCORAHS'""" % (lon, lat,
           id, state)
    mcursor.execute( sql )

mcursor.close()
MESOSITE.commit()
