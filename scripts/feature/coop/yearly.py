import psycopg2
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT extract(year from day + '5 months'::interval) as yr,
 sum(snow) from alldata_ia where station = 'IA2203' 
 and day > '1885-07-01' GROUP by yr ORDER by yr ASC""")

years = []
snow = []

for row in cursor:
    if row[1] is None:
        print row
        continue
    years.append( row[0] -1 )
    snow.append( row[1] )
    
years = np.array(years)
snow = np.array(snow)
avgsnow = np.average(snow)
maxsnow = np.max(snow) + 3
    
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1, 1)
ax.bar(years -0.5, snow, fc='b', ec='b')
ax.set_title("Des Moines 1885-2012 Yearly Snowfall")
ax.set_ylabel("Total Snowfall [inch]")
ax.set_xlabel("Year of Winter Season Start")
ax.set_ylim(0, maxsnow)
ax.set_xlim(1884,2013)
ax.grid(True)
ax.axhline( avgsnow, lw=1.5, c='k')
txt = ax.text(1890, avgsnow+0.4, "%.1f" % (avgsnow,), color='white')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="k")])
y2 = ax.twinx()
y2.set_ylim(0, maxsnow / avgsnow * 100.0)
y2.set_ylabel("Percent of Longterm Average [%]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')