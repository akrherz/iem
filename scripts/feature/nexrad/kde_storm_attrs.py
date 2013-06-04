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
  SELECT x(geom), y(geom) from nexrad_attributes_2013
  where nexrad = 'DMX' and tvs != 'NONE'
""")
for row in cursor:
    lons.append( row[0] )
    lats.append( row[1] )
    
X, Y = numpy.mgrid[reference.IA_WEST:reference.IA_EAST:100j, 
                   reference.IA_SOUTH:reference.IA_NORTH:100j]
positions = numpy.vstack([X.ravel(), Y.ravel()])
values = numpy.vstack([lons, lats])
kernel = stats.gaussian_kde(values)
Z = numpy.reshape(kernel(positions).T, X.shape)

m = MapPlot(sector='iowa',
            title='DMX NEXRAD Tornado Vortex Signature Kernel Density Estimate',
            subtitle='Jan 2013- May 2013')

m.pcolormesh(X, Y, Z, numpy.arange(0,1,.1), cmap=plt.cm.gist_earth_r,
            latlon=True)

xs, ys = m.map(-93.72, 41.72)
m.ax.scatter(xs, ys, marker='o', zorder=20, s=50, color='k')

#xs, ys = m.map(lons, lats)
#m.ax.scatter(xs, ys, marker='+', zorder=20, s=100, color='k')

m.drawcounties()
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