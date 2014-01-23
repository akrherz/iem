import iemdb
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select extract(year from day + '4 months'::interval) as yr,
  sum(case when low < 0 Then 1 else 0 end),
  sum(case when low < 0 and (month > 6 or sday < '0124') then 1 else 0 end)
  from alldata_ia where
  station = 'IA8706' GROUP by yr ORDER by yr ASC
""")

years = []
precip = []
precip2 = []
for row in ccursor:
    years.append( row[0] )
    precip.append( float(row[1])  )
    precip2.append( float(row[2])  )

precip[-1] += 2
precip2[-1] += 2

import matplotlib.pyplot as plt
import numpy

precip = numpy.array(precip)
avg = numpy.average(precip)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='b', ec='b', label='After 24 Jan')
bars = ax.bar(years - 0.4, precip2, fc='tan', ec='tan', label='Prior to 24 Jan')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
#for bar in bars:
#    if bar.get_height() >= 25:
#        ax.text(bar.get_x()-0.3, bar.get_height()+1, "%.0f" % (bar.get_x()+0.4,),
#                ha='center')
ax.axhline(avg, lw=2.0, color='k', zorder=2, label='Season Ave: %.1f' % (avg,))

ax.set_xlabel("*2014 thru 23 Jan, year of spring shown")
ax.set_xlim(1892.5, 2014.5)
#ax.text(1980,2.75, "2013 second driest behind 1940", ha='center',
#  bbox=dict(facecolor='#FFFFFF'))
ax.grid(True)
ax.legend(loc=2)
ax.set_ylabel(r"Days over winter season")
ax.set_title("1893-2013 Waterloo Days with Low below 0$^\circ$F")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
