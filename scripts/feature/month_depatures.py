import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

climate = []
ccursor.execute("""
 SELECT avg(d), month from (SELECT year, month, avg((high+low)/2.0) as d from alldata_ia 
 where station = 'IA0000' and day < '2012-08-01'
 GROUP by year, month) as foo GROUP by month ORDER by month ASC
""")
for row in ccursor:
  climate.append( row[0] )

ccursor.execute("""
 SELECT avg(d), month from (SELECT year, month, avg((high+low)/2.0) as d from alldata_ia 
 where station = 'IA0000' and month = 8 and sday < '0816'
 GROUP by year, month) as foo GROUP by month ORDER by month ASC
""")
row = ccursor.fetchone()
august = row[0]


diff = []
ccursor.execute("""
 SELECT year, month, avg((high+low)/2.0) from alldata_ia where 
 station = 'IA0000' and year > 2006 and day < '2012-08-16'
 GROUP by year, month ORDER by year, month ASC
""")
for row in ccursor:
    if row[0] == 2012 and row[1] == 8:
        diff.append( row[2] - august )
    else:
        diff.append( row[2] - climate[ row[1] -1] )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("Iowa Monthly Average Temperature Departure")

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
ax.set_ylabel("Departure $^{\circ}\mathrm{F}$")
ax.set_xlabel("* Aug 2012 total thru 15 Aug")
ax.grid(True)
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(-0.5, len(diff)+0.5)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
