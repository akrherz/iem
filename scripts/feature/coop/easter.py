from dateutil.easter import easter
import datetime
import numpy as np

import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""SELECT day, high from alldata_ia where station = 'IA2203'""")
data = {}
for row in cursor:
    data[ row[0] ] = row[1]

highs = []

for yr in range(1880,2014):
    e = easter(yr)
    highs.append( data[e] )
highs.append( 84 )
highs = np.array(highs)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.bar(np.arange(1880,2015), highs, fc='b', ec='b')
for i, bar in enumerate(bars):
    if highs[i] >= highs[-1]:
        ax.text( 1880+i, highs[i] + 1, "%s\n%s" % (highs[i], 1880+i), ha='center', va='bottom')
        bars[i].set_facecolor('r')
        bars[i].set_edgecolor('r')
ax.grid(True)
ax.set_ylim(0,95)
ax.set_xlim(1879,2015)
ax.set_title("1880-2014 Des Moines Easter High Temperature")
ax.set_ylabel("High Temperature $^\circ$F")

fig.savefig('test.png')
