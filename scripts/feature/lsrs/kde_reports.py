from scipy import stats
import psycopg2
import numpy
from pyiem import reference
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt

POSTGIS = psycopg2.connect(database='postgis', user='nobody', host='iemdb')
cursor = POSTGIS.cursor()

lons = []
lats = []
cursor.execute("""
  SELECT x(geom), y(geom), valid,
  x(ST_Transform(geom,2163)), y(ST_Transform(geom,2163)) from lsrs 
  where  typetext = 'HAIL'
  and x(geom) between %s and %s and y(geom) between %s and %s
  and magnitude >= 1 ORDER by valid ASC
""", (reference.MW_WEST - 3, reference.MW_EAST + 3, reference.MW_SOUTH - 3,
      reference.MW_NORTH + 3))
recent = []
for row in cursor:
    valid = row[2]
    dup = False
    for r in recent:
        tdelta = (valid - r[0]).days * 86400. + (valid - r[0]).seconds
        if tdelta > 15*60:
            recent.remove(r)
            continue
        ddelta = ((row[3] - r[1])**2 + (row[4] - r[2])**2)**.5
        if ddelta < 15000 and tdelta < 15*60:
            dup = True
    if dup:
        #print 'DUP', row
        continue
    recent.append([valid, row[3], row[4]])
    lons.append( row[0] )
    lats.append( row[1] )
    
X, Y = numpy.mgrid[reference.MW_WEST:reference.MW_EAST:50j, 
                   reference.MW_SOUTH:reference.MW_NORTH:50j]
positions = numpy.vstack([X.ravel(), Y.ravel()])
values = numpy.vstack([lons, lats])
kernel = stats.gaussian_kde(values)
Z = numpy.reshape(kernel(positions).T, X.shape)

m = MapPlot(sector='midwest',
            title='Local Storm Reports of Hail (1+") :: Kernel Density Estimate',
            subtitle='2003 - May 2013, gaussian kernel, 15min/15km duplicate rule applied')

m.pcolormesh(X, Y, Z, numpy.arange(0,0.006,.0003), cmap=plt.cm.gist_earth_r,
            latlon=True)

#xs, ys = m.map(-93.72, 41.72)
#m.ax.scatter(xs, ys, marker='o', zorder=20, s=50, color='k')

#xs, ys = m.map(lons, lats)
#m.ax.scatter(xs, ys, marker='+', zorder=20, s=100, color='k')

#m.drawcounties()
m.postprocess(filename='test.png')

"""

fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(numpy.rot90(Z), cmap=plt.cm.gist_earth_r,
          extent=[reference.IA_WEST,reference.IA_EAST, reference.IA_SOUTH,
                  reference.IA_NORTH])
ax.plot(lons, lats, 'k.', markersize=2)
ax.set_title("2013 Des Moines NEXRAD MESO Kernel Density Estimate")
fig.savefig('test.png')
"""