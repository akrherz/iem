
import urllib2
import time
import iemdb
import simplejson
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
mcursor2 = MESOSITE.cursor()

mcursor.execute("""
 SELECT network, x(geom) as lon, y(geom) as lat, elevation, id from stations 
 WHERE (elevation < -990 or elevation is null)""")

for row in mcursor:
    elev = row[3]
    lat = row[2]
    lon = row[1]
    sid = row[4]
    network = row[0]
    #r = urllib2.urlopen('http://weather.gladstonefamily.net/cgi-bin/wx-get-elevation.pl?lat=%s&lng=%s' % (lat,lon)).read()
    r = urllib2.urlopen('http://sampleserver4.arcgisonline.com/'+
            'ArcGIS/rest/services/Elevation/ESRI_Elevation_World/'+
            'MapServer/exts/ElevationsSOE/ElevationLayers/1/'+
            'GetElevationAtLonLat?lon=%s&lat=%s&f=pjson' % (lon,lat)).read()
    #tokens =  re.findall(' ele="([0-9\.\-]*)" ', r)
    #if len(tokens) == 0:
    #  print 'ERROR WITH %s La: %s Lo: %s Res: %s' % (id, lat, lon, r)
    #  continue
    #newelev = float(tokens[0])
    json = simplejson.loads(r)
    newelev = json.get('elevation', -999)
    
    print "%7s %s OLD: %s NEW: %.3f" % (sid, network, elev, newelev)
    mcursor2.execute("""UPDATE stations SET elevation = %s WHERE id = %s 
        and network = %s""", (newelev, sid, network))
    time.sleep(2)

mcursor2.close()
MESOSITE.commit()
