import iemdb
import math
import re
import psycopg2.extras
postgis = iemdb.connect('postgis', bypass=True)
pcursor = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)
pcursor2 = postgis.cursor(cursor_factory=psycopg2.extras.DictCursor)

def rotate(x,y,rad):
    return (x * math.cos(-rad) - y * math.sin(-rad)), (x * math.sin(-rad) + y * math.cos(-rad))

def dir2ccwrot(dir):
    # Convert to CCW
    dir = 360 - dir
    # Convert to zero being east
    dir += 90
    # Convert to bearing
    dir += 180
    if dir > 360:
        dir -= 360
    return dir

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

pcursor.execute("""
  SELECT x(ST_Centroid(ST_Transform(geom,2163))) as center_x,  
    y(ST_Centroid(ST_Transform(geom,2163))) as center_y, *, ST_AsText(geom) as gtext,
     x(ST_CEntroid(geom)) as lon, y(ST_Centroid(geom)) as lat,
     ST_AsText(ST_Transform(geom,2163)) as projtext
    from warnings
    WHERE issue > '2008-01-01' and gtype = 'P' and significance = 'W' and 
    phenomena in ('SV','TO') LIMIT 1
""")
for row in pcursor:
    tokens = re.findall(r'TIME...MOT...LOC [0-9]{4}Z ([0-9]{1,3})DEG ([0-9]{1,3})KT', row['report'])
    (dir, sknt) = tokens[0]
    smps = float(sknt) * 0.514
    dir = float(dir)
    # This is the from angle, need to rotate 180 to get the to angle
    angle = dir2ccwrot( dir )
    rad = math.radians(angle)
    x0 = row['center_x']
    y0 = row['center_y']
    warnX.append(x0)
    warnY.append(y0)
    for pr in (row['projtext'].replace("MULTIPOLYGON(((", "").replace(")))", "")).split(","):
        x,y = pr.split()
        polyX.append(float(x))
        polyY.append(float(y))
    # Compute travel line!
    majorX.append( x0 - math.cos(angle)*smps*1800.)
    majorX.append( x0 + math.cos(angle)*smps*1800.)
    majorY.append( y0 - math.sin(angle)*smps*1800.)
    majorY.append( y0 + math.sin(angle)*smps*1800.)
    minorX.append( x0 - math.cos(angle+math.pi/2.)*smps*1800.)
    minorX.append( x0 + math.cos(angle+math.pi/2.)*smps*1800.)
    minorY.append( y0 - math.sin(angle+math.pi/2.)*smps*1800.)
    minorY.append( y0 + math.sin(angle+math.pi/2.)*smps*1800.)
    
    # Find LSRs
    pcursor2.execute("""
    SELECT distinct *, x(ST_Transform(geom,2163)) as x, y(ST_Transform(geom,2163)) as y,
        x(geom) as lon, y(geom) as lat
         from lsrs w WHERE 
         geom && ST_Buffer(SetSrid(GeometryFromText('%s'),4326),0.01) and 
         contains(ST_Buffer(SetSrid(GeometryFromText('%s'),4326),0.01), geom) 
         and  wfo = '%s' and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= 1) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
         and valid >= '%s' and valid <= '%s' 
         ORDER by valid ASC
    """ % (row['gtext'], row['gtext'], row['wfo'], row['issue'], row['expire']))
    for row2 in pcursor2:
        lx = row2['x']
        ly = row2['y']
        lsrX.append(lx)
        lsrY.append(ly)
        deltax = lx - x0
        deltay = ly - y0
        deltaX.append(deltax)
        deltaY.append(deltay)
        # rotate!
        xP, yP = rotate(deltax,deltay, rad)
        rlsrX.append(xP)
        rlsrY.append(yP)
        print 'X0: %.1f Y0: %.1f X: %.1f Y: %.1f DX: %.1f DY: %.1f Dir %.0f Rotation: %.1f xP: %.1f yP: %.1f' % (
                                            x0, y0, lx, ly, deltax, deltay, dir, angle,
                                                                       xP, yP)
    
import matplotlib.pyplot as plt
import numpy
fig = plt.figure()
ax = fig.add_subplot(211)

ax.scatter( warnX, warnY, color='r' )
ax.scatter( lsrX, lsrY, color='b' )
ax.plot(polyX, polyY, color='r')
ax.plot(majorX, majorY, color='black')
ax.plot(minorX, minorY, color='black')

ax2 = fig.add_subplot(212)
ax2.scatter(rlsrX, rlsrY, color='b')
#ax2.scatter(deltaX, deltaY)
ax2.scatter([0,], [0,], color='r')
#ax2.plot( numpy.arange(0,360), map(dir2ccwrot, numpy.arange(0,360)))

fig.savefig('test.png')