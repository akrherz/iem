"""Hit up ESRIs elevation REST service to compute a station elevation

"""
import urllib2
import time
import psycopg2
import json
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

mcursor.execute("""
    SELECT network, ST_x(geom) as lon, ST_y(geom) as lat, elevation, id
    from stations WHERE (elevation < -990 or elevation is null)""")

for row in mcursor:
    elev = row[3]
    lat = row[2]
    lon = row[1]
    sid = row[4]
    network = row[0]
    r = urllib2.urlopen((
        'http://sampleserver4.arcgisonline.com/'
        'ArcGIS/rest/services/Elevation/ESRI_Elevation_World/'
        'MapServer/exts/ElevationsSOE/ElevationLayers/1/'
        'GetElevationAtLonLat?lon=%s&lat=%s&f=pjson') % (lon, lat)).read()
    j = json.loads(r)
    newelev = j.get('elevation', -999)

    print "%7s %s OLD: %s NEW: %.3f" % (sid, network, elev, newelev)
    mcursor2.execute("""
        UPDATE stations SET elevation = %s WHERE id = %s
        and network = %s""", (newelev, sid, network))
    time.sleep(2)

mcursor2.close()
MESOSITE.commit()
