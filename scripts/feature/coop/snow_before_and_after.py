import psycopg2
import numpy as np
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 SELECT extract(year from day + '6 months'::interval) as yr, sum(snow),
 sum(case when sday > '0306' and month < 7 then snow else 0 end) from
 alldata_ia where station = 'IA2203' and snow >= 0 GROUP by yr ORDER by yr ASC
""")

years = []
total = []
after = []
for row in cursor:
    years.append( row[0] )
    total.append( row[1] )
    after.append( row[2] )
    
years = np.array(years)
total = np.array(total)
after = np.array(after)
percentages =  (total - after)/total * 100.0

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(2,1, sharex=True)

ax[0].set_title("1890-2014 Des Moines Snowfall before/after 6 March")
ax[0].set_ylabel("% of Season Snow by 6 March")
ax[0].bar(years[:-1]-0.4, percentages[:-1], ec='b', fc='b')
ax[0].axhline( np.average(percentages), color='k')
txt = ax[0].text(1900, np.average(percentages), "%.1f%%" % (np.average(percentages),),
                 fontsize=18)
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])
ax[0].grid(True)

ax[1].bar(years-0.4, after, ec='b', fc='b')
ax[1].axhline( np.average(after), color='k')
ax[1].set_xlim(1890,2015)
ax[1].grid(True)
ax[1].set_ylabel("After 6 March Snowfall [inch]")
txt = ax[1].text(1900, np.average(after), "%.1f inch" % (np.average(after),),
                 fontsize=18)
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')