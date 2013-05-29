import iemdb
import numpy
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

elnino = []
mcursor.execute("""SELECT anom_34 from elnino where monthdate >= '2007-01-01'""")
for row in mcursor:
    elnino.append( float(row[0]) )

elnino = numpy.array(elnino)

climate = []
ccursor.execute("""
 SELECT avg(d), month from (SELECT year, month, sum(precip) as d from alldata_ia 
 where station = 'IA0200' and day < '2013-01-01'
 GROUP by year, month) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
  climate.append( float(row[0]) )

diff = []
ccursor.execute("""
 SELECT year, month, sum(precip) from alldata_ia where 
 station = 'IA0200' and year > 2006 
 GROUP by year, month ORDER by year, month ASC
""")
for row in ccursor:
    diff.append( float(row[2]) - climate[ row[1] -1] )

diff = numpy.array(diff)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Ames Monthly Precipitation Departure\nEl Nino 3.4 Index")
#"""
xticks = []
xticklabels = []
for i in range(0, len(diff),6):
  ts = mx.DateTime.DateTime(2007,1,1) + mx.DateTime.RelativeDateTime(months=i)
  if ts.month == 1:
    fmt = "%b\n%Y"
  else:
    fmt = "%b"
  xticklabels.append( ts.strftime(fmt) )
  xticks.append( i )

bars = ax.bar(numpy.arange(0, len(diff))-0.4, diff, fc='b', ec='b')
for bar in bars:
  if bar.get_xy()[1] < 0:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')

ax2 = ax.twinx()

ax2.plot(numpy.arange(0, len(elnino)), elnino, zorder=2, color='k', lw=2.0)
ax2.set_ylabel("El Nino 3.4 Index (line)")

ax.set_ylabel("Precip Departure [inch] (bars)")
ax.set_xlabel("* Thru 28 May 2013")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(-0.5, len(diff)+0.5)
ax.set_ylim(-8,8)
"""
import scipy.stats
for i in range(0,12):
    print len(diff[i:-2]), len(elnino[:-(i+1)])
    print i, numpy.corrcoef(diff[i:-2], elnino[:-(i+1)])[0,1]
#ax.scatter(diff[2:], elnino[:-1])
"""
fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
