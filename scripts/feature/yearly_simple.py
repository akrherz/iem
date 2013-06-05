import iemdb
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select year, max(high), min(high) from alldata_ia where station = 'IA2203' and 
 month = 6 and sday < '0606' GROUP by year ORDER by year ASC
""")

years = []
highs = []
lows = []
for row in ccursor:
  years.append( row[0] )
  highs.append( row[1] )
  lows.append( row[2] )

import matplotlib.pyplot as plt
import numpy

highs = numpy.array(highs)
lows = numpy.array(lows)
avg = numpy.average(highs)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, highs - lows, bottom=lows, fc='b', ec='b')
#ax.plot([1893,2013],[avg,avg], lw=2.0, color='k', zorder=2)
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
for i, bar in enumerate(bars):
  if highs[i] <= highs[-1]:
    bar.set_facecolor('r')
    bar.set_edgecolor('r')
    txt= ax.text(years[i], lows[i]-2, "%s\n%.0f" % (years[i],highs[i],), ha='center', va='top') 
    txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground="w")])

#ax.set_xlabel("*2013 thru 29 May")
ax.set_xlim(1877.5, 2013.5)
ax.grid(True)
ax.set_ylabel(r"High Temperature $^\circ$F")
ax.set_title("1879-2013 1-5 June Des Moines Daily High Temperature Range")

fig.savefig('test.svg')

import iemplot
iemplot.makefeature('test')
