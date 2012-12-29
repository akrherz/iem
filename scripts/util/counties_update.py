"""
My purpose in life is to take the NWS AWIPS Geodata Counties Shapefile and 
dump them into the NWSChat PostGIS database!
"""
from osgeo import ogr
from osgeo import _ogr
import sys
import os
import urllib2
import iemdb
import psycopg2.extras
mydb = iemdb.connect('postgis')
mcursor = mydb.cursor(cursor_factory=psycopg2.extras.DictCursor)

# Get the name of the file we wish to download
if len(sys.argv) == 1:
    print 'ERROR: You need to specify the file date to download'
    print 'Example:  python counties_update.py 01dec10'
    sys.exit(0)

DATESTAMP = sys.argv[1]

def Area(feat, *args):
    """
    Backport a feature from the future!
    """
    return _ogr.Geometry_GetArea(feat, *args)

# Change Directory to /tmp, so that we can rw
os.chdir('/tmp')

url = urllib2.Request('http://www.weather.gov/geodata/catalog/county/data/c_%s.zip' % (
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
f = ogr.Open('c_%s.shp' % (DATESTAMP,))
GEO_TYP = 'C'
lyr = f.GetLayer(0)

ugcs = {}

feat = lyr.GetNextFeature()
while feat is not None:
  state = feat.GetField('STATE')
  fips  = feat.GetField('FIPS')
  cwa = feat.GetField('CWA')
  name  = feat.GetField('COUNTYNAME')
  tz = feat.GetField('TIME_ZONE')
  if tz is None:
      tz = ""
  if state is None or fips is None:
    print "Nulls: State [%s] FIPS [%s] Name [%s]" % (state, fips, name)
    feat = lyr.GetNextFeature()
    continue


  geo = feat.GetGeometryRef()
  area = Area(geo)
  wkt = geo.ExportToWkt()

  ugc = "%s%s%s" % (state, GEO_TYP, str(fips)[-3:])
  if ugcs.has_key(ugc):
      if area < ugcs[ugc]:
          print 'Skipping %s [area: %s], since we had a previously bigger one' % (ugc, area)
          feat = lyr.GetNextFeature()
          continue
  ugcs[ugc] = area

  mcursor.execute("""DELETE from nws_ugc WHERE ugc = '%s'
        and wfo = '%s' """ % (ugc, cwa))
  sql = """INSERT into nws_ugc (polygon_class, ugc, name, state, wfo,
          time_zone, geom, centroid) VALUES ('%s','%s','%s','%s','%s',
          '%s', ST_Multi(ST_SetSRID(ST_GeomFromEWKT('%s'),4326)),
          ST_Centroid( ST_SetSRID(ST_GeomFromEWKT('%s'),4326) ) )""" % (
          GEO_TYP, ugc, name.replace("'", " "), state, cwa,
          tz, wkt,
          wkt )
  #print 'Updating [%s] [%s] [%s]' % (cwa, ugc, name)
  mcursor.execute(sql)


  feat = lyr.GetNextFeature()

mydb.commit()
mcursor.close()
mydb.close()
print 'Done!'
