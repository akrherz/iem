import psycopg2
import numpy as np

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
 select year, avg(high) from alldata_ia 
 where station = 'IA2203' and sday >= '0714' and sday < '0719' 
 GROUP by year ORDER by year ASC
 """)

years = []
data = []

for row in cursor:
    years.append( row[0]  )
    data.append( float(row[1]) )

years.append(2014)
data.append( np.average([76,68,74,78,78]))

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
    if data[i] < 79 or data[i] > 95:
        txt = ax.text(years[i], data[i]+(0.075 if years[i] != 1881 else -0.45), "%s" % (years[i],), 
                      color='k', fontsize=14,
                      ha=('left' if years[i] < 1910 else 'right'), va='bottom')
        txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="yellow")])

bars[-1].set_facecolor('yellow')
bars[-1].set_edgecolor('yellow')
        
ax.set_title("1879-2013 Des Moines Average High Temp (14-19 July)")
ax.set_ylabel("Average Daily High $^\circ$F")
ax.set_xlabel("* 2014 forecasted values of 76,68,74,78,78")
ax.set_ylim(70, 105.5)
ax.set_xlim(1878.5,2014.5)
ax.grid(True)
ax.axhline( avgdata, lw=2.5, c='white')
ax.axhline( avgdata, lw=1, c='k')
txt = ax.text(1969.5, avgdata, "%.1f" % (avgdata,), color='red', fontsize=15, va='center')
txt.set_path_effects([PathEffects.withStroke(linewidth=2,
                                                 foreground="white")])

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
