"""
Used 20130401
"""
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

counts = []
years = []

pcursor.execute("""
 SELECT yr, count(*) from 
 (SELECT distinct extract(year from issue) as yr, wfo, phenomena, 
 eventid from warnings where phenomena in ('TO')
 and significance = 'W' and
 extract(month from issue) < 4) as foo GROUP by yr""")
for row in pcursor:
    years.append( row[0] )
    counts.append( row[1] )
import numpy
years2 = numpy.array( years )
ax.bar(years2 -0.4, counts)
ax.set_title("1986-2014 NWS Issued United States Tornado Warnings")
ax.set_ylabel("January thru March Total")
ax.set_xlim(1985.5,2014.5)
ax.grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
