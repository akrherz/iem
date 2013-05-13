import iemdb
import math
import re
import psycopg2.extras
import matplotlib.pyplot as plt
import numpy
import mx.DateTime
import iemplot
import pyproj
P2163 = pyproj.Proj(init='epsg:2163')
postgis = iemdb.connect('postgis', bypass=True)
pcursor = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor2 = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)

def rotate(x,y,rad):
    return (x * math.cos(-rad) - y * math.sin(-rad)), (x * math.sin(-rad) + y * math.cos(-rad))

def dir2ccwrot(dir):
    # Convert to CCW
    if dir >= 270 and dir <= 360:
        return 0 - (dir - 270)
    if dir >= 180 and dir < 270:
        return 270 - dir
    if dir >= 90 and dir < 180:
        return 180 - (dir - 90)
    if dir >= 0 and dir < 90:
        return 180 + (90 - dir )

#for i in range(0,360,10):
#    print i, dir2ccwrot( i )

warnX = []
warnY = []
lsrX = []
lsrY = []
rlsrX = []
rlsrY = []
polyX = []
polyY = []
majorX = []
minorX = []
minorY = []
majorY = []
deltaX = []
deltaY = []
dT = []
dXT = []
dDist = []
offsetX = []
offsetY = []
#output = open('xy.dat', 'w')

pcursor.execute("""
  SELECT x(ST_Centroid(ST_Transform(geom,2163))) as center_x,  
    y(ST_Centroid(ST_Transform(geom,2163))) as center_y, *, ST_AsText(geom) as gtext,
     x(ST_CEntroid(geom)) as lon, y(ST_Centroid(geom)) as lat,
     ST_AsText(ST_Transform(geom,2163)) as projtext
    from warnings
    WHERE issue > '2008-01-01' and issue < '2012-01-01' and gtype = 'P' 
    and significance = 'W' and 
    phenomena in ('TO') and wfo = 'GID'
""") # and wfo = 'DMX' and eventid = 13 and phenomena= 'TO' and issue < '2009-01-01'
i = 0
for row in pcursor:
    issue = mx.DateTime.strptime(str(row['issue'])[:16], '%Y-%m-%d %H:%M')
    expire = mx.DateTime.strptime(str(row['expire'])[:16], '%Y-%m-%d %H:%M')
    i += 1
    if i % 1000 == 0:
        print 'Done', i
    tokens = re.findall(r'TIME...MOT...LOC [0-9]{4}Z ([0-9]{1,3})DEG ([0-9]{1,3})KT ([0-9]+) ([0-9]+)', row['report'])
    if len(tokens) == 0:
        print 'FAIL', row['wfo'], row['eventid'], row['issue']
        continue
    (dir, sknt, lat100, lon100) = tokens[0]
    lon = 0 - (int(lon100) / 100.)
    lat = int(lat100) / 100.
    xTML, yTML = P2163(lon, lat)
    if float(sknt) == 0:
        continue
    smps = float(sknt) * 0.514
    dir = float(dir)
    # This is the from angle, need to rotate 180 to get the to angle
    angle = dir2ccwrot( dir )
    rad = math.radians(angle)
    print dir, angle, rad
    
    xTML2 = xTML + math.cos(rad)*smps*1800. # 30 min
    yTML2 = yTML + math.sin(rad)*smps*1800. # 30 min
    ulX = xTML + math.cos(rad+math.pi/2.)*10000.
    ulY = yTML + math.sin(rad+math.pi/2.)*10000. # 10km "north"
    llX = xTML - math.cos(rad+math.pi/2.)*10000.
    llY = yTML - math.sin(rad+math.pi/2.)*10000. # 10km "south"
    urX = xTML2 + math.cos(rad+math.pi/2.)*10000.
    urY = yTML2 + math.sin(rad+math.pi/2.)*10000. # 10km "north"
    lrX = xTML2 - math.cos(rad+math.pi/2.)*30000.
    lrY = yTML2 - math.sin(rad+math.pi/2.)*30000. # 30km "south"

    
    # Find LSRs
    sql = """
    INSERT into bot_warnings(issue, expire, gtype, wfo,
    geom, eventid, phenomena, significance) VALUES ('%s', '%s',
    'P', '%s', 
    ST_Transform(GeomFromText('SRID=2163;MULTIPOLYGON(((%s %s, %s %s, %s %s, %s %s, %s %s)))'),4326),
    %s, '%s', '%s')
    """ % (row['issue'].strftime("%Y-%m-%d %H:%M"), row['expire'].strftime("%Y-%m-%d %H:%M"),
           row['wfo'], llX, llY, ulX, ulY, urX, urY, lrX, lrY, llX, llY,
           row['eventid'], row['phenomena'], row['significance'])
    #print sql
    pcursor2.execute( sql )

pcursor2.close()
postgis.commit()
