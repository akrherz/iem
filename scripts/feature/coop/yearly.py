import psycopg2
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT year, sum(gddxx(50,86,high,low)) from alldata_ia where station = 'IA0200' and sday > '0414' and sday < '0514' GROUP by year ORDER by year
 ASC""")

years = []
data = []

for row in cursor:
    years.append( row[0]  )
    data.append( float(row[1]) )
    
years = np.array(years)
data = np.array(data)
avgdata = np.average(data)
    
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1, 1)
bars = ax.bar(years -0.5, data, fc='brown', ec='brown')
for i, bar in enumerate(bars):
    if data[i] < avgdata:
        bar.set_facecolor('darkblue')
        bar.set_edgecolor('darkblue')
    if data[i] >= 900:
        txt = ax.text(years[i], data[i]+(0.075 if years[i] != 1881 else -0.45), "%s" % (years[i],), 
                      color='k', fontsize=14,
                      ha=('left' if years[i] < 1901 else 'right'), va='bottom')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

ax.set_title("Ames 1970-2014 15 April - 13 May Growing Degree Days\n(base 50, ceiling 86)")
ax.set_ylabel("Growing Degree Days")
#ax.set_xlabel("* 2013 thru 14 Nov")
#ax.set_ylim(0, 12.5)
ax.set_xlim(1969.5,2014.5)
ax.grid(True)
ax.axhline( avgdata, lw=2.5, c='white')
ax.axhline( avgdata, lw=1, c='k')
txt = ax.text(1969.5, avgdata, "%.1f" % (avgdata,), color='red', fontsize=15, va='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="white")])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
