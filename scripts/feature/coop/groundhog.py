import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT extract(year from day + '4 months'::interval) as yr, 
 sum(case when snow >= 0.1 then 1 else 0 end),
 sum(case when snow >= 0.1 and sday > '0201' and sday < '0701' then 1 else 0 end)
 from alldata_ia where 
 station = 'IA0200' 
 and day > '1899-09-01' and day < '2012-06-01' GROUP by yr ORDER by yr ASC
""")

years = []
total = []
after = []
for row in ccursor:
    years.append( row[0] )
    total.append( row[1] )
    after.append( row[2] )

years = numpy.array(years)
total = numpy.array(total)
after = numpy.array(after)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(2,1)
ax[0].scatter(total - after, after)
ax[0].grid(True)
ax[0].set_title("1900-2012 Ames Daily Snowfall Events")
ax[0].set_xlabel("Days with snow before 2 Feb")
ax[0].set_ylabel("Days with snow after 2 Feb ")
ax[0].set_xlim(-0.1,30)

ax[1].bar(years, after, ec='b', fc='b')
ax[1].set_xlim(1899.5, 2012.5)
ax[1].grid(True)
ax[1].set_ylabel("Days with snow after 2 Feb")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
