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
 SELECT avg(d), month from (SELECT year, month, avg((high+low)/2.0) as d from alldata_ia 
 where station = 'IA2203' and day < '2012-10-01'
 GROUP by year, month) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
  climate.append( float(row[0]) )

diff = []
ccursor.execute("""
 SELECT year, month, avg((high+low)/2.0) from alldata_ia where 
 station = 'IA2203' and year > 2006 
 GROUP by year, month ORDER by year, month ASC
""")
for row in ccursor:
    if row[0] == 2012 and row[1] == 18:
        diff.append( row[2] - august )
    else:
        diff.append( float(row[2]) - climate[ row[1] -1] )

diff = numpy.array(diff)

import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Des Moines Monthly Average Temperature Departure")
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

bars = ax.bar(numpy.arange(0, len(diff))-0.4, diff, fc='r', ec='r')
for bar in bars:
  if bar.get_xy()[1] < 0:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')

#ax.plot(numpy.arange(0, len(elnino)), elnino)

ax.set_ylabel("Departure $^{\circ}\mathrm{F}$")
ax.set_xlabel("* Oct 2012 total thru 30 Aug")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(-0.5, len(diff)+0.5)
"""
import scipy.stats
for i in range(0,12):
    print len(diff[i:-2]), len(elnino[:-(i+1)])
    print i, numpy.corrcoef(diff[i:-2], elnino[:-(i+1)])[0,1]
#ax.scatter(diff[2:], elnino[:-1])
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
