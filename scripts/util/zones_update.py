"""
My purpose in life is to take the NWS AWIPS Geodata Zones Shapefile and 
dump them into the NWSChat PostGIS database!
"""
from osgeo import ogr
from osgeo import _ogr
import psycopg2
import sys
import os
import datetime
import pytz
import urllib2
import zipfile
POSTGIS = psycopg2.connect(database='postgis', host='iemdb')
cursor = POSTGIS.cursor()

def Area(feat, *args):
    """
    Backport a feature from the future!
    """
    return _ogr.Geometry_GetArea(feat, *args)

# Get the name of the file we wish to download
if len(sys.argv) != 5:
    print 'ERROR: You need to specify the file date to download and date'
    print 'Example:  python zones_update.py z_01dec10 2010 12 01'
    sys.exit(0)

DATESTAMP = sys.argv[1]
TS = datetime.datetime(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
TS = TS.replace(tzinfo=pytz.timezone("UTC"))

# Change Directory to /tmp, so that we can rw
os.chdir('/tmp')

zipfn = "%s.zip" % (DATESTAMP,)
if not os.path.isfile(zipfn):
    url = urllib2.Request(('http://www.weather.gov/geodata/catalog/wsom/'
                       +'data/%s') % (zipfn,))
    print 'Downloading %s ...' % (zipfn,)
    o = open(zipfn, 'wb')
    o.write(urllib2.urlopen(url).read())
    o.close()

print 'Unzipping'
zipfp = zipfile.ZipFile(zipfn, 'r')
shpfn = None
for name in zipfp.namelist():
    print '    Extracting %s' % (name,)
    o = open(name, 'wb')
    o.write(zipfp.read(name))
    o.close()
    if name[-3:] == 'shp':
        shpfn = name

print 'Processing'
# Now we are ready to dance!
f = ogr.Open(shpfn)
lyr = f.GetLayer(0)

ugcs = {}
GEO_TYP = 'Z'
feat = lyr.GetNextFeature()
countnoop = 0
countnew = 0
while feat is not None:
    if zipfn[:2] in ('mz', 'oz', 'hz'):
        state = ""
        name = feat.GetField("NAME")
        cwa = feat.GetField('WFO')
        ugc = feat.GetField("ID")
        zone = ugc[-3:]
    else:
        state = feat.GetField('STATE')
        zone  = feat.GetField('ZONE')
        cwa = feat.GetField('CWA')
        name  = feat.GetField('NAME')
        ugc = "%s%s%s" % (state, GEO_TYP, zone)
    if state is None or zone is None:
        print "Nulls: State [%s] Zone [%s] Name [%s]" % (state, zone, name)
        feat = lyr.GetNextFeature()
        continue


    geo = feat.GetGeometryRef()
    if not geo:
        feat = lyr.GetNextFeature()
        continue
    area = Area(geo)
    wkt = geo.ExportToWkt()

    if ugcs.has_key(ugc):
        if area < ugcs[ugc]:
            print 'Skipping %s [area: %s], since we had a previously bigger one' % (ugc, area)
            feat = lyr.GetNextFeature()
            continue
    ugcs[ugc] = area

    # OK, lets see if this UGC is new
    cursor.execute("""SELECT ugc from ugcs where ugc = %s
        and end_ts is null and name = %s and 
        geom = ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326))""", 
        (ugc, name, wkt))
    
    # NOOP
    if cursor.rowcount == 1:
        countnoop += 1
        feat = lyr.GetNextFeature()
        continue
        
    # Go find the previous geom and truncate the time
    cursor.execute("""
        UPDATE ugcs SET end_ts = %s WHERE ugc = %s and end_ts is null""", 
            (TS, ugc))
    
    # Finally, insert the new geometry    
    cursor.execute("""
    INSERT into ugcs (ugc, name, state, begin_ts, wfo, geom)
    VALUES (%s, %s, %s, %s, %s,
    ST_Multi(ST_SetSRID(ST_GeomFromEWKT(%s),4326)))
    """, (ugc, name, state, TS, cwa, wkt))
    countnew += 1
    feat = lyr.GetNextFeature()

print 'NOOP: %s NEW: %s' % (countnoop, countnew)

cursor.execute("""UPDATE ugcs SET simple_geom = ST_Simplify(geom, 0.01)""")
cursor.execute("""UPDATE ugcs SET centroid = ST_Centroid(geom)""")


cursor.close()
POSTGIS.commit()
POSTGIS.close()
print 'Done!'
