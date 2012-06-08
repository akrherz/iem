import iemdb
import numpy as np
import numpy.ma

COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

ccursor.execute("""
 SELECT year, min(high), min(low) from alldata_ia where station = 'IA1319'
 and year < 2012 and month = 5 GROUP by year
""")
high_hits = numpy.ma.zeros( (31,), 'f')
low_hits = numpy.ma.zeros( (31,), 'f')
for row in ccursor:
    ccursor2.execute("""
    SELECT day from alldata_ia where year = %s and month = 5 and 
    high = %s and station = 'IA1319'
    """, (row[0], row[1]))
    for row2 in ccursor2:
        high_hits[row2[0].day-1] += 1.0 / ccursor2.rowcount

    ccursor2.execute("""
    SELECT day from alldata_ia where year = %s and month = 5 and 
    low = %s and station = 'IA1319'
    """, (row[0], row[2]))
    for row2 in ccursor2:
        low_hits[row2[0].day-1] += 1.0 / ccursor2.rowcount

high_hits.mask = numpy.where(high_hits == 0, True, False)
low_hits.mask = numpy.where(low_hits == 0, True, False)
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2,1, sharex=True)

#res = ax.contourf( data, extend='max')
ax[0].set_title("Cedar Rapids (1893-2011) Frequency of Day in May\nHaving Coldest High Temperature of May")
ax[0].set_ylabel("Years (ties split)")

ax[0].grid(True)
ax[0].bar(numpy.arange(1,32) - 0.4, high_hits)
ax[0].set_xlim(0.5, 31.5)

ax[1].set_title("Having Coldest Low Temperature of May")
ax[1].set_ylabel("Years (ties split)")
ax[1].grid(True)
ax[1].set_xlabel("Day of May")
ax[1].bar(numpy.arange(1,32) - 0.4, low_hits)


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test') 
