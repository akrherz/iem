"""
My purpose in life is to take the NWS AWIPS Geodata Zones Shapefile and 
dump them into the NWSChat PostGIS database!
"""
from osgeo import ogr
import pg
import sys
import os
import urllib2
postgis = pg.connect('postgis', 'iemdb')

# Get the name of the file we wish to download
if len(sys.argv) == 1:
    print 'ERROR: You need to specify the file date to download'
    print 'Example:  python zones_update.py 01dec10'
    sys.exit(0)

DATESTAMP = sys.argv[1]

# Change Directory to /tmp, so that we can rw
os.chdir('/tmp')

url = urllib2.Request('http://www.weather.gov/geodata/catalog/wsom/data/z_%s.zip' % (
                                                                        DATESTAMP,))
print 'Downloading....'
try:
    fp = urllib2.urlopen(url)
    zip = fp.read()
    o = open('%s.zip' % (DATESTAMP,), 'wb')
    o.write(zip)
    o.close()
except:
    print 'An exception was encountered attempting to download the file.'
    print 'Please check that this URL is valid'
    print url
    sys.exit()

print 'Unzipping'
os.system("unzip %s.zip" % (DATESTAMP,))

print 'Processing'
# Now we are ready to dance!
f = ogr.Open('z_%s.shp' % (DATESTAMP,))
GEO_TYP = 'Z'
lyr = f.GetLayer(0)

ugcs = {}

feat = lyr.GetNextFeature()
while feat is not None:
  state = feat.GetField('STATE')
  zone  = feat.GetField('ZONE')
  cwa = feat.GetField('CWA')
  name  = feat.GetField('NAME')
  tz = feat.GetField('TIME_ZONE')
  if tz is None:
      tz = ""
  if state is None or zone is None:
    print "Nulls: State [%s] Zone [%s] Name [%s]" % (state, zone, name)
    feat = lyr.GetNextFeature()
    continue


  geo = feat.GetGeometryRef()
  area = geo.Area()
  wkt = geo.ExportToWkt()

  ugc = "%s%s%s" % (state, GEO_TYP, zone)
  if ugcs.has_key(ugc):
      if area < ugcs[ugc]:
          print 'Skipping %s [area: %s], since we had a previously bigger one' % (ugc, area)
          feat = lyr.GetNextFeature()
          continue
  ugcs[ugc] = area

  postgis.query("""DELETE from nws_ugc WHERE ugc = '%s'
        and wfo = '%s' """ % (ugc, cwa))
  sql = """INSERT into nws_ugc (polygon_class, ugc, name, state, wfo,
          time_zone, geom, centroid) VALUES ('%s','%s','%s','%s','%s',
          '%s', ST_Multi(ST_SetSRID(ST_GeomFromEWKT('%s'),4326)),
          ST_Centroid( ST_SetSRID(ST_GeomFromEWKT('%s'),4326) ) )""" % (
          GEO_TYP, ugc, name.replace("'", " "), state, cwa,
          tz, wkt,
          wkt )
  #print 'Updating [%s] [%s] [%s]' % (cwa, ugc, name)
  postgis.query(sql)


  feat = lyr.GetNextFeature()

print 'Done!'
