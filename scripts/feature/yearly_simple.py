import iemdb
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('asos', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select extract(year from valid) as yr, sum(sknt * dur) / sum(dur) 
 from 
 (select valid, 
 extract(epoch from (valid - lag(valid) OVER (ORDER by valid ASC)))::numeric as dur, 
 sknt  from alldata WHERE sknt >= 0 and station = 'DSM') as foo 
 WHERE extract(month from valid) = 1 and extract(day from valid) < 21
 GROUP by yr ORDER by yr ASC
""")

years = []
precip = []
for row in ccursor:
    years.append( row[0] )
    precip.append( float(row[1]) * 1.15 )

import matplotlib.pyplot as plt
import numpy

precip = numpy.array(precip)
avg = numpy.average(precip)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='b', ec='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
#for bar in bars:
#    if bar.get_height() >= 25:
#        ax.text(bar.get_x()-0.3, bar.get_height()+1, "%.0f" % (bar.get_x()+0.4,),
#                ha='center')
ax.axhline(avg, lw=2.0, color='k', zorder=2)

#ax.set_xlabel("*2013 thru 29 May")
ax.set_xlim(1935.5, 2014.5)
#ax.text(1980,2.75, "2013 second driest behind 1940", ha='center',
#  bbox=dict(facecolor='#FFFFFF'))
ax.grid(True)
ax.set_ylabel(r"Average Wind Speed [mph]")
ax.set_title("1-20 January 1936-2014 Des Moines Average Wind Speed")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
