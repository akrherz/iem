import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT avg(high), avg(low) from alldata where stationid = 'ia2203' and month = 7 
 and year > 1892
""")
row = ccursor.fetchone()
avgHigh = row[0]
avgLow = row[1]

highs = []
lows = []
ccursor.execute("""
 SELECT year, avg(high), avg(low) from alldata where stationid = 'ia2203' and month = 7
 GROUP by year ORDER by year ASC
""")
for row in ccursor:
    highs.append( float(row[1] - avgHigh) )
    lows.append( float(row[2] - avgLow) )

import numpy
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(311)
ax.set_title("Des Moines July Temperatures")

bars = ax.bar(numpy.arange(1893,2012) - 0.4, highs, facecolor='r', edgecolor='r')
for bar in bars:
  if bar.get_xy()[1] < 0:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax.set_xlim( 1892.5,2011.5 )
ax.set_ylabel("Daily High Temp.\n Departure $^{\circ}\mathrm{F}$")
ax.grid(True)

ax = fig.add_subplot(312)

bars= ax.bar(numpy.arange(1893,2012) - 0.4, lows, facecolor='r', edgecolor='r')
for bar in bars:
  if bar.get_xy()[1] < 0:
    bar.set_facecolor('b')
    bar.set_edgecolor('b')
ax.set_xlim( 1892.5,2011.5 )
ax.set_ylabel("Daily Low Temp.\n Departure $^{\circ}\mathrm{F}$")
ax.grid(True)

ax = fig.add_subplot(313)

ax.scatter( lows, highs )
ax.scatter( lows[-1], highs[-1], facecolor='r', label='2011' )
ax.set_xlim( -10,10)
ax.set_ylim( -15,15)
ax.plot([-15,15],[-15,15])
ax.set_ylabel("Daily High Temp.\n Departure $^{\circ}\mathrm{F}$")
ax.set_xlabel("Low Temp. Departure $^{\circ}\mathrm{F}$")
import scipy.stats
ax.text( 7,-14, "$R^{2}$ %.1f" % ((scipy.stats.corrcoef(lows, highs)[0,1]) ** 2,))
ax.grid(True)
ax.legend(loc=2)

fig.savefig('test.ps')
