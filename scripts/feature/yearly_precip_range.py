import iemdb, network
import numpy

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select year, sum(case when high >= 100 then 1 else 0 end), max(high)
 from alldata_ia where station = 'IA2203' GROUP by year ORDER By year ASC
""")
years = []
count = []
maxv = []
for row in ccursor:
    years.append( row[0] )
    count.append( float(row[1])  )
    maxv.append( float(row[2])  )

count[-1] = 1
maxv[-1] = 101

years = numpy.array(years)

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(2,1)
bars = ax[0].bar( years - 0.4, count, 
        facecolor='red', ec='red', zorder=1)
bars[-1].set_facecolor('green')
bars[-1].set_edgecolor('green')
ax[0].set_title("Des Moines Days over 100$^{\circ}\mathrm{F}$ [1886-2012]")
ax[0].grid(True)
ax[0].set_ylabel('Days')
ax[0].set_xlim(1885.5,2013.5)

bars = ax[1].bar( years - 0.4, maxv, 
        facecolor='red', ec='red', zorder=1)
bars[-1].set_facecolor('green')
bars[-1].set_edgecolor('green')
ax[1].set_title("Des Moines Maximum Temperature [1886-2012]")
ax[1].grid(True)
ax[1].set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax[1].set_xlim(1885.5,2013.5)
ax[1].set_ylim(90,110)
ax[1].set_xlabel("* 2012 Data thru 27 June", color='g')


fig.savefig('test.ps')
iemplot.makefeature('test')
