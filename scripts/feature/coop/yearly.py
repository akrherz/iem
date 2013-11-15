import psycopg2
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT year, sum(case when precip >= 1.25 then 1 else 0 end)
 from alldata_ia where station = 'IA2203' 
 GROUP by year ORDER by year ASC""")

years = []
data = []

for row in cursor:
    years.append( row[0]  )
    data.append( row[1] )
    
years = np.array(years)
data = np.array(data)
avgdata = np.average(data)
    
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

(fig, ax) = plt.subplots(1, 1)
bars = ax.bar(years -0.5, data, fc='darkblue', ec='darkblue')
for i, bar in enumerate(bars):
    if data[i] < avgdata:
        bar.set_facecolor('brown')
        bar.set_edgecolor('brown')
    if data[i] >= 9:
        txt = ax.text(years[i], data[i]+(0.075 if years[i] != 1881 else -0.45), "%s" % (years[i],), 
                      color='k', fontsize=14,
                      ha=('left' if years[i] < 1901 else 'right'), va='bottom')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

ax.set_title("Des Moines 1878-2013 Calendar Days with 1.25+ inch precip")
ax.set_ylabel("Days per year")
ax.set_xlabel("* 2013 thru 14 Nov")
ax.set_ylim(0, 12.5)
ax.set_xlim(1877,2013.5)
ax.grid(True)
ax.axhline( avgdata, lw=2.5, c='white')
ax.axhline( avgdata, lw=1, c='k')
txt = ax.text(1869.5, avgdata, "%.1f" % (avgdata,), color='red', fontsize=15, va='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="white")])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')