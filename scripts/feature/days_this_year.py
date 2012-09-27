import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

ccursor.execute("""SELECT year, max(high) from alldata_ia WHERE
 station = 'IA2203' and year < 2012 GROUP by year ORDER by year ASC""")

years = []
days = []
for row in ccursor:
    years.append( row[0] )
    ccursor2.execute("""SELECt * from alldata_ia where
    station = 'IA2203' and year = 2012 and high > %s""" % (row[1],))
    days.append( ccursor2.rowcount )

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(numpy.array(years)-0.5, days, fc='r', ec='r')
ax.set_xlim(1886,2013)
ax.grid(True)
ax.set_ylabel("2012 Days Warmer than Given Year")
ax.set_xlabel("Chart average: %.1f days" % (numpy.average(numpy.array(days)),))
ax.set_title("Des Moines: 1 Jan - 1 Aug 2012 Days with warmer high temperature\nthan warmest daily high temperature for that year (1886-2011)")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
