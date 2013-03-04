import iemdb
import numpy
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
 SELECT year,
 sum(case when snow >= 4 then 1 else 0 end),
 sum(case when snow >= 6 then 1 else 0 end)
 from alldata_ia where 
 station = 'IA0200' and sday >= '0202' and month < 7
 and day > '1899-09-01' and day < '2012-06-01' GROUP by year ORDER by year ASC
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

(fig, ax) = plt.subplots(1,1, figsize=[10,7])
ax.bar(years, total, zorder=1, fc='r', label='4+ inch')
ax.bar(years, after, zorder=2, fc='g', label='6+ inch')
ax.grid(True)
ax.set_title("1900-2012 Ames Snowfall Events after 2 February")
ax.set_ylabel("Days")
ax.set_xlim(1899,2013)
ax.legend()

fig.savefig('test.png')
