"""
My purpose in life is to take the NWS AWIPS Geodata Zones Shapefile and 
dump them into the NWSChat PostGIS database!
"""
from osgeo import ogr
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
    print 'Example:  python zones_update.py 01dec10'
    sys.exit(0)

DATESTAMP = sys.argv[1]

# Change Directory to /tmp, so that we can rw
os.chdir('/tmp')

url = urllib2.Request('http://www.weather.gov/geodata/catalog/wsom/data/mz%s.zip' % (
                                                                        DATESTAMP,))
print 'Downloading....'
try:
    fp = urllib2.urlopen(url)
    zipdata = fp.read()
    o = open('%s.zip' % (DATESTAMP,), 'wb')
    o.write(zipdata)
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
f = ogr.Open('mz%s.shp' % (DATESTAMP,))
GEO_TYP = 'Z'
lyr = f.GetLayer(0)

ugcs = {}

feat = lyr.GetNextFeature()
while feat is not None:
    zone  = feat.GetField('ID')
    cwa = feat.GetField('WFO')
    name  = feat.GetField('NAME')
    tz = ""
    state = zone[:2]
    if state is None or zone is None:
        print "Nulls: State [%s] Zone [%s] Name [%s]" % (state, zone, name)
        feat = lyr.GetNextFeature()
        continue

    geo = feat.GetGeometryRef()
    if not geo:
        feat = lyr.GetNextFeature()
        continue
    area = geo.Area()
    wkt = geo.ExportToWkt()

    if ugcs.has_key(zone):
        if area < ugcs[zone]:
            print 'Skipping %s [area: %s], since we had a previously bigger one' % (zone, area)
            feat = lyr.GetNextFeature()
            continue
    ugcs[zone] = area

    mcursor.execute("""DELETE from nws_ugc WHERE ugc = '%s'
        and wfo = '%s' """ % (zone, cwa))
    sql = """INSERT into nws_ugc (polygon_class, ugc, name, state, wfo,
          time_zone, geom, centroid) VALUES ('%s','%s','%s','%s','%s',
          '%s', ST_Multi(ST_GeomFromText('%s', 4326)),
          ST_Centroid( ST_GeomFromText('%s',4326) ) )""" % (
          GEO_TYP, zone, name.replace("'", " "), state, cwa,
          tz, wkt,wkt )
    mcursor.execute(sql)


    feat = lyr.GetNextFeature()

mydb.commit()
mcursor.close()
mydb.close()
print 'Done!'
