import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

climate = []
ccursor.execute("""
 SELECT avg(sum), month from (SELECT year, month, sum(precip) from alldata_ia where station = 'IA2203' 
 GROUP by year, month) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
  climate.append( row[0] )

diff = []
ccursor.execute("""
 SELECT year, month, sum(precip) from alldata_ia where station = 'IA2203' and year > 2004
 GROUP by year, month ORDER by year, month ASC
""")
for row in ccursor:
    diff.append( row[2] - climate[ row[1] -1] )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Des Moines Monthly Precipitation Departures")

xticks = []
xticklabels = []
for i in range(0, len(diff),6):
  ts = mx.DateTime.DateTime(2005,1,1) + mx.DateTime.RelativeDateTime(months=i)
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
ax.set_ylabel("Precipitation Departure [inch]")
ax.set_xlabel("* Oct 2011 total thru 24 Oct")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(-0.5, len(diff)+0.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
