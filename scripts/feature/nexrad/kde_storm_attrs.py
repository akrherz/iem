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
  SELECT x(geom), y(geom), valid from nexrad_attributes_log
  where nexrad in ('DMX','ARX','DVN','OAX','FSD','EAX','MPX') and tvs != 'NONE'
""")
minvalid = None
maxvalid = None
for row in cursor:
    if minvalid is None or row[2] < minvalid:
        minvalid = row[2]
    if maxvalid is None or row[2] > maxvalid:
        maxvalid = row[2]
    lons.append(row[0])
    lats.append(row[1])

X, Y = numpy.mgrid[reference.IA_WEST:reference.IA_EAST:100j,
                   reference.IA_SOUTH:reference.IA_NORTH:100j]
positions = numpy.vstack([X.ravel(), Y.ravel()])
values = numpy.vstack([lons, lats])
kernel = stats.gaussian_kde(values)
Z = numpy.reshape(kernel(positions).T, X.shape)

m = MapPlot(sector='iowa',
            title='NEXRAD Tornado Vortex Signature Reports',
            subtitle=('%s - %s, (TVS storm attribute present)'
                      ) % (minvalid.strftime("%d %b %Y"),
                           maxvalid.strftime("%d %b %Y")))

# m.pcolormesh(X, Y, Z, numpy.arange(0,.11,.01), cmap=plt.cm.gist_earth_r,
#            latlon=True)

xs, ys = m.map([-93.72, -96.37, -91.18, -90.57, -96.72],
               [41.72, 41.32, 43.82, 41.6, 43.58])
m.ax.scatter(xs, ys, marker='o', zorder=20, s=100, color='r')

xs, ys = m.map(lons, lats)
m.ax.scatter(xs, ys, marker='+', zorder=20, s=40, color='k')

m.drawcounties()
m.postprocess(filename='test.png')

fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(numpy.rot90(Z), cmap=plt.get_cmap('gist_earth_r'),
          extent=[reference.IA_WEST, reference.IA_EAST,
                  reference.IA_SOUTH, reference.IA_NORTH])
ax.plot(lons, lats, 'k.', markersize=2)
ax.set_title("2013 Des Moines NEXRAD MESO Kernel Density Estimate")
fig.savefig('test.png')
