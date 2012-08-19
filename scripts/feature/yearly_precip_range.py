import iemdb, network
import numpy

COOP = iemdb.connect('postgis', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select extract(year from date) as yr, sum(case when extract(doy from date) < 232 then 1 else 0 end), sum(case when extract(doy from date) > 231 then 1 else 0 end) from (select distinct date(issue - '7 hours'::interval) from warnings where phenomena = 'TO' and ugc ~* 'IAC' and significance = 'W') as foo GROUP by yr ORDER by yr ASC
""")
years = []
prior = []
total = []
for row in ccursor:
    years.append( row[0] )
    prior.append( float(row[1])  )
    total.append( float(row[1] + row[2])  )

years = numpy.array(years)

import matplotlib.pyplot as plt
import iemplot
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

fig, ax = plt.subplots(1,1)
bars = ax.bar( years - 0.4, total, 
        facecolor='g', ec='g', zorder=1, label='After 19 Aug')
bars = ax.bar( years - 0.4, prior, 
        facecolor='lightblue', ec='lightblue', zorder=2, label='Prior 19 Aug')
for i in range(len(total)):
    ax.text(1986+i, total[i]+0.5, "%.0f" % (total[i],), ha='center')

ax.set_title("Days with Tornado Warning Issued in Iowa (1986-2012)")
ax.grid(True)
ax.set_xlabel("thru 19 August 2012")
ax.set_ylabel('Number of Days (7 AM - 7 AM)')
ax.set_xlim(1985.5,2013.5)
ax.legend(loc='best')


fig.savefig('test.ps')
iemplot.makefeature('test')
