
from matplotlib import pyplot as plt
import iemdb
import numpy

d2010 = []
dclimo = []
dbconn = iemdb.connect('coop', bypass=True)
c = dbconn.cursor()
c.execute("SELECT precip, year from alldata WHERE year > 1999 and precip > 0.005 and month > 3 and month < 9 and stationid = 'ia0200'")
for row in c:
  if row[1] < 2010:
    dclimo.append( row[0] )
  else:
    d2010.append( row[0] )
c.close()
dbconn.close()

bins, edges = numpy.histogram( d2010, 25 )
bins2, edges = numpy.histogram( dclimo, edges )
print numpy.diff(edges)

ax = plt.subplot(111)
ax.bar( edges[:-1], bins , width=0.154, color='b', label="2010")
ax.bar( edges[:-1] + 0.154, bins2 / 10.0, width=0.154, color='r', label="2000-2009")
#n, bins, patches = ax.hist( data, 25, normed=True)
#print bins
plt.savefig("test.png")
