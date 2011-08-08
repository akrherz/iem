import iemdb
import math
import re
import psycopg2.extras
import matplotlib.pyplot as plt
import numpy
import mx.DateTime
import pyproj
P2163 = pyproj.Proj(init='epsg:2163')
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
    WHERE issue > '2008-01-01' and issue < '2011-01-01' and gtype = 'P' and significance = 'W' and 
    phenomena in ('TO')
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
    x0 = row['center_x']
    y0 = row['center_y']
    offsetX.append( (x0 - xTML) / 1000. )
    offsetY.append( (y0 - yTML) / 1000. )
    #warnX.append(x0)
    #warnY.append(y0)
    #for pr in (row['projtext'].replace("MULTIPOLYGON(((", "").replace(")))", "")).split(","):
    #    x,y = pr.split()
    #    polyX.append(float(x))
    #    polyY.append(float(y))
    # Compute travel line!
    #majorX.append( x0 - math.cos(angle)*smps*1800.)
    #majorX.append( x0 + math.cos(angle)*smps*1800.)
    #majorY.append( y0 - math.sin(angle)*smps*1800.)
    #majorY.append( y0 + math.sin(angle)*smps*1800.)
    #minorX.append( x0 - math.cos(angle+math.pi/2.)*smps*1800.)
    #minorX.append( x0 + math.cos(angle+math.pi/2.)*smps*1800.)
    #minorY.append( y0 - math.sin(angle+math.pi/2.)*smps*1800.)
    #minorY.append( y0 + math.sin(angle+math.pi/2.)*smps*1800.)
    
    # Find LSRs
    pcursor2.execute("""
    SELECT distinct *, x(ST_Transform(geom,2163)) as x, y(ST_Transform(geom,2163)) as y,
        x(geom) as lon, y(geom) as lat
         from lsrs_%s w WHERE 
         geom && ST_Buffer(SetSrid(GeometryFromText('%s'),4326),0.01) and 
         contains(ST_Buffer(SetSrid(GeometryFromText('%s'),4326),0.01), geom) 
         and  wfo = '%s' and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= 1) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
         and valid >= '%s' and valid <= '%s'  and type in ('T')
         ORDER by valid ASC
    """ % (row['issue'].year, row['gtext'], row['gtext'], row['wfo'], row['issue'], row['expire']))
    for row2 in pcursor2:
        valid = mx.DateTime.strptime(str(row2['valid'])[:16], '%Y-%m-%d %H:%M')
        lx = row2['x']
        ly = row2['y']
        #lsrX.append(lx)
        #lsrY.append(ly)
        #deltax = lx - x0
        #deltay = ly - y0
        deltax = lx - xTML
        deltay = ly - yTML
        deltat = (valid - issue).minutes

        #deltaX.append(deltax)
        #deltaY.append(deltay)
        # rotate!
        xP, yP = rotate(deltax,deltay, rad)
        x_t =  (smps * deltat * 60.0)  # How far along x axis we should be
        deltax_t = xP - x_t
        dT.append( deltat )
        dXT.append( deltax_t / 1000.)
        dDist.append( ((deltax_t*deltax_t + yP*yP)**0.5) / 1000.)
        #print 'DeltaT: %.1f DeltaTx: %.3f SMPS: %.1f' % (deltat, deltax_t, smps)
        #rlsrX.append(xP / 1000.)
        #rlsrY.append(yP / 1000.)
        rlsrX.append(xP / smps)
        rlsrY.append(yP / smps)
        #output.write("%.1f,%.1f\n" % (xP, yP))
        #print 'X0: %.1f Y0: %.1f X: %.1f Y: %.1f DX: %.1f DY: %.1f Dir %.0f Rotation: %.1f xP: %.1f yP: %.1f' % (
        #                                    x0, y0, lx, ly, deltax, deltay, dir, angle,
        #                                                               xP, yP)
#output.close()
#sys.exit()

fig = plt.figure()

ax = fig.add_subplot(111)
#maxV = max([max(rlsrX),0-min(rlsrX),max(rlsrY),0-min(rlsrX)])
maxV = 60.*60 # one hour
#H2, xedges, yedges = numpy.histogram2d(numpy.array(dDist), numpy.array(dT), 
#                                       range=[[0,60],[0,60]], bins=(60, 60))
#H2, xedges, yedges = numpy.histogram2d(numpy.array(offsetX), numpy.array(offsetY), 
#                                       range=[[-60,60],[-60,60]], bins=(60, 60))
H2, xedges, yedges = numpy.histogram2d(numpy.array(dXT), numpy.array(dT), 
                                       range=[[-60,60],[0,60]], bins=(60, 60))
#H2, xedges, yedges = numpy.histogram2d(numpy.array(rlsrX), numpy.array(rlsrY), 
#                                       range=[[0-maxV,maxV],[0-maxV,maxV]], bins=(60, 60))
#H2 = numpy.ma.array(H2)
H2 = numpy.ma.array(H2.transpose())
H2.mask = numpy.where( H2 < 1, True, False)
extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
res = ax.imshow(H2,  extent=extent, interpolation='nearest')
#ax.set_ylim(-60,60)
ax.grid(True)
#ax.set_xticks( numpy.arange(-3600,3601,600))
#ax.set_xticklabels( numpy.arange(-60,61,10))
#ax.set_yticks( numpy.arange(-3600,3601,600))
#ax.set_yticklabels( numpy.arange(-60,61,10))
ax.set_xlabel("Distance from Moving Line along path [km]")
ax.set_ylabel("Increasing Time [minutes]")
ax.set_title("TOR Report Displacement from Tracking Line\nfrom the moving TIME..MOT..LOC (1 Jan 2008-22 Jul 2011)")
clr = fig.colorbar(res)
clr.ax.set_ylabel("Reports")

"""
fig.subplots_adjust(hspace=0.3,left=0.2,right=0.8)
ax = fig.add_subplot(211)

ax.set_title("Example Storm Based Warning (UTM Space)")
ax.scatter( warnX, warnY, color='r', label='Centroid' )
ax.scatter( lsrX, lsrY, color='b' ,label='LSRs')
ax.plot(polyX, polyY, color='r', label='SBW')
ax.plot(majorX, majorY, color='black', label="Major")
ax.plot(minorX, minorY, color='tan', label="Minor")
ax.set_xlabel("Easting [m]")
ax.set_ylabel("Northing [m]")
ax.legend(loc=(0.99,0.2))
ax.grid(True)

ax2 = fig.add_subplot(212)
ax2.set_title("Rotated Relative to SBW Centroid")
ax2.scatter(rlsrX, rlsrY, color='b')
#ax2.scatter(deltaX, deltaY)
ax2.scatter([0,], [0,], color='r')
#ax2.plot( numpy.arange(0,360), map(dir2ccwrot, numpy.arange(0,360)))
ax2.set_ylabel("Y-displacement [km]")
ax2.set_xlabel("X-displacement [km]")
ax2.grid(True)
"""
fig.savefig('test.png')
