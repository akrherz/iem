from scipy import stats
import psycopg2
import numpy
from pyiem import reference
from pyiem.plot import MapPlot
import matplotlib.pyplot as plt

POSTGIS = psycopg2.connect(database='postgis', user='nobody', host='iemdb')
cursor = POSTGIS.cursor()

cursor.execute("""
 SELECT drct, sknt, extract(doy from valid) from nexrad_attributes_2012 WHERE
 nexrad = 'DMX' and sknt > 0
""")

drct = []
sknt = []
doy = []
for row in cursor:
    drct.append( row[0] )
    sknt.append( row[1] )
    doy.append( row[2] )
(fig, ax) = plt.subplots(2,1)

X, Y = numpy.mgrid[0:360:36j, 
                   0:70:35j]
positions = numpy.vstack([X.ravel(), Y.ravel()])
values = numpy.vstack([drct, sknt])
kernel = stats.gaussian_kde(values)
Z = numpy.reshape(kernel(positions).T, X.shape)

ax[0].imshow(Z, extent=[0,360,0,70])
ax[1].scatter(doy, drct)

fig.savefig('test.png')