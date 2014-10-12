import iemdb
import math
import Ngl
import numpy
import random
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()
pcursor2 = POSTGIS.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

stations = {}

def dir22(u,v):
  if (v == 0):
    v = 0.000000001
  dd = math.atan(u / v)
  ddir = (dd * 180.00) / math.pi

  if (u > 0 and v > 0 ): # First Quad
    ddir = 180 + ddir
  elif (u > 0 and v < 0 ): # Second Quad
    ddir = 360 + ddir
  elif (u < 0 and v < 0 ): # Third Quad
    ddir = ddir
  elif (u < 0 and v > 0 ): # Fourth Quad
    ddir = 180 + ddir

  return math.fabs(ddir)

def uv(sped, drct2):
  dirr = drct2 * math.pi / 180.00
  s = math.sin(dirr)
  c = math.cos(dirr)
  u = round(- sped * s, 2)
  v = round(- sped * c, 2)
  return u, v

reports = []
dirs = []
sknts = []

# Sample a few watches
pcursor.execute("""
  SELECT issued, expired, ST_AsText(w.geom) as geo,
  xmax(w.geom), xmin(w.geom), ymax(w.geom), ymin(w.geom) from watches w, states s where 
  ST_Contains(s.the_geom, ST_Centroid(w.geom)) and s.state_abbr = 'IA' 
  and type = 'TOR' and issued > '2002-01-01'
""")

for row in pcursor:
    # Do verification
    pcursor2.execute("""
    SELECT distinct city, county, geom from lsrs_%s WHERE
    ST_Contains(ST_SetSrid(GeometryFromText('%s'),4326), geom) and
    valid BETWEEN '%s'::timestamp and '%s'::timestamp and type = 'T'
    """ % (row[0].year, row[2], row[0], row[1]))
    r = pcursor2.rowcount
    # Find stations we care about
    ids = []
    sql = """
    SELECT id, x(geom) as lon, y(geom) as lat from stations s
    WHERE ST_Contains(ST_SetSrid(GeometryFromText('%s'),4326), s.geom) 
    and (network ~* 'ASOS' or network = 'AWOS')
    """ % (row[2], )
    mcursor.execute(sql)
    for row2 in mcursor:
        ids.append( row2[0])
        stations[row2[0]] = {'lat': row2[2], 'lon': row2[1]}

    # Now we construct a query of the ASOS database
    lats = []
    lons = []
    U = []
    V = []
    sql = """
    SELECT distinct station, sknt, drct from t%s d
    WHERE  
    d.station in (%s)
    and d.valid BETWEEN '%s'::timestamp - '30 minutes'::interval and 
    '%s'::timestamp + '30 minutes'::interval and sknt >= 0 and drct >= 0
    """ % (row[0].year, str(tuple(ids))[1:-1], row[0], row[0])
    acursor.execute(sql)
    if acursor.rowcount < 4:
        print 'ASOS Missing!', row[0], row[1]
        continue
        
    for row2 in acursor:
        u,v = uv(row2[1] * 0.514, row2[2])
        lats.append( stations[row2[0]]['lat'] + random.random() * 0.01)
        lons.append( stations[row2[0]]['lon'] + random.random() * 0.01)
        U.append( u )
        V.append( v )
        
    xaxis = numpy.arange(row[4], row[3], 0.25)
    yaxis = numpy.arange(row[6], row[5], 0.25)
    Ugrid = Ngl.natgrid(lons, lats, U, xaxis, yaxis)
    Vgrid = Ngl.natgrid(lons, lats, V, xaxis, yaxis)
    avgU = numpy.average(Ugrid)
    avgV = numpy.average(Vgrid)
    avgDir = dir22(avgU,avgV)
    reports.append(r)
    dirs.append(  math.radians(avgDir) )
    sknts.append( ((avgU ** 2) + (avgV ** 2))**0.5)
    print '%s,%s,%s' % (r, math.radians(avgDir), ((avgU ** 2) + (avgV ** 2))**0.5)

reports = numpy.array(reports)

dirs = numpy.array( dirs )
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, polar=True)

theta_angles = numpy.arange(0, 360, 45)
theta_labels = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
ax.set_thetagrids(angles=theta_angles, labels=theta_labels)

res = ax.scatter( - dirs + math.pi/2.,  sknts, c=reports, s=reports)
fig.colorbar(res)


fig.savefig('test.png')