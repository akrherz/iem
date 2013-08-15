import iemdb
import matplotlib.patheffects as PathEffects

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 select extract(year from day) as yr, 
 sum(case when pday >= 0.5 then 1 else 0 end) / count(*)::numeric from 
  (select ia.day, dsm.pday, ia.max, dsm.pday / ia.max as ratio from 
   (select day, max(precip) from alldata_ia where  
     precip >= 1 and
     station in (SELECT distinct station from alldata_ia where year = 1951 and
     precip > 0) and month in (6,7,8) GROUP by day)  as ia, 
   (select day, precip as pday from alldata_ia where station = 'IA2203'
    and year > 1950) as dsm 
  WHERE ia.day = dsm.day ) as foo 
 GROUP by yr ORDER by yr ASC
""")

years = []
precip = []
for row in ccursor:
    years.append( row[0] )
    precip.append( float(row[1]) * 100.0)

import matplotlib.pyplot as plt
import numpy

precip = numpy.array(precip)
avg = numpy.average(precip)

(fig, ax) = plt.subplots(1,1)
years = numpy.array(years)
bars = ax.bar(years - 0.4, precip, fc='b', ec='b')
bars[-1].set_facecolor('r')
bars[-1].set_edgecolor('r')
for bar in bars:
    if bar.get_height() >= 25:
        ax.text(bar.get_x()-0.3, bar.get_height()+1, "%.0f" % (bar.get_x()+0.4,),
                ha='center')
ax.plot([1893,2013],[avg,avg], lw=2.0, color='k', zorder=2)

#ax.set_xlabel("*2013 thru 29 May")
ax.set_xlim(1950.5, 2013.5)
#ax.text(1980,2.75, "2013 second driest behind 1940", ha='center',
#  bbox=dict(facecolor='#FFFFFF'))
ax.grid(True)
ax.set_ylabel(r"Frequency [%]")
ax.set_title("[Jun-Jul-Aug 1951-2013] Somewhere in Iowa gets 1+ in/dy,\nDid Des Moines report 0.5+ inch rainfall?")
ax.set_xlabel("*2013 thru 15 August")
fig.savefig('test.ps')

import iemplot
iemplot.makefeature('test')
