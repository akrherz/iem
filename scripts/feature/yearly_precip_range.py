import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select extract(year from day) as yr, max(avg) from (select one.day, (one.high + two.high + three.high + one.low + two.low + three.low) / 6.0 as avg from (select day, high, low from alldata_ia where station = 'IA2203') as one, (select day + '1 day'::interval as day, high, low from alldata_ia where station = 'IA2203') as two, (select day + '2 days'::interval as day, high, low from alldata_ia where station = 'IA2203') as three WHERE one.day = two.day and two.day = three.day ORDER by avg DESC) as foo GROUP by yr ORDER by yr ASC
""")
years = []
count = []
maxv = []
for row in ccursor:
    years.append( row[0] )
    maxv.append( float(row[1])  )

years = numpy.array(years)

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(1,1)
bars = ax.bar( years - 0.4, maxv, 
        facecolor='g', ec='g', zorder=1)
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
ax.set_title("Des Moines Warmest 3 Day Period by Year [1880-2012]\nAverage High Temperature")
ax.grid(True)
ax.set_xlabel("thru 6 July 2012")
ax.set_ylabel('Daily Average High Temp $^{\circ}\mathrm{F}$')
ax.set_xlim(1879.5,2013.5)
ax.set_ylim(85,110)

fig.savefig('test.ps')
iemplot.makefeature('test')
