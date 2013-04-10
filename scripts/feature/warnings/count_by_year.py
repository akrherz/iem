"""
Used 20130401
"""
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1)

import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

counts = []
years = []

pcursor.execute("""
 SELECT yr, count(*) from 
 (SELECT distinct extract(year from issue) as yr, wfo, phenomena, 
 eventid from warnings where substr(ugc,1,2) = 'IA' and phenomena in ('SV','TO')
 and significance = 'W' and
 extract(month from issue) = 3) as foo GROUP by yr""")
for row in pcursor:
    years.append( row[0] )
    counts.append( row[1] )
import numpy
years2 = numpy.array( years )
ax[0].bar(years2 -0.4, counts)
ax[0].set_title("1986-2013 Iowa Severe T'Storm + Tornado Warnings")
ax[0].set_ylabel("March Total")
ax[0].set_xlim(1985.5,2013.5)
ax[0].grid(True)

yeartot = []
march = []

pcursor.execute("""
 SELECT yr, count(*) from 
 (SELECT distinct extract(year from issue) as yr, wfo, phenomena, 
 eventid from warnings where substr(ugc,1,2) = 'IA' and phenomena in ('SV','TO')
 and significance = 'W' and issue < '2013-01-01') as foo GROUP by yr""")
for row in pcursor:
    if row[0] in years:
        idx = years.index( row[0] )
        march.append( counts[idx] )
    else:
        march.append( 0 )
    yeartot.append( row[1] )

ax[1].scatter(march, yeartot)
for m,y in zip(march, yeartot):
    if m > 30 or y > 1000:
        ax[1].text(m, y+25, "%.0f" % (years[counts.index(m)],), va='bottom',
                ha='center')
ax[1].set_ylim(bottom=0)
ax[1].set_xlim(left=-2)
ax[1].grid(True)
ax[1].set_xlabel("March Total")
ax[1].set_ylabel("Total for Year")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
