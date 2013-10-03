"""
Used 20130401
"""
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

import psycopg2
POSTGIS = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
pcursor = POSTGIS.cursor()

def get(state):
    pcursor.execute("""
     SELECT week, count(*) from 
     (SELECT distinct extract(year from issue) as year, 
     round((extract(doy from issue)::numeric - 1.0) / 7.,0) as week from
     warnings where phenomena = 'TO' and significance = 'W' and substr(ugc,1,2) = %s
     and issue < '2013-01-01') as foo 
     WHERE week < 53 GROUP by week ORDER by week ASC
    """, (state,))
    weeks = []
    counts = []
    for row in pcursor:
        weeks.append( row[0]  )
        counts.append( row[1] / 27.0 * 100.0)
    return weeks, counts

import numpy as np

c = ['r', 'b', 'g', 'k']
markers = ['s', '+', 'o', 'x']
for i, state in enumerate(['IA', 'OK', 'AL', 'TX']):
    counts = np.zeros((53,))
    ws, cs = get(state)
    counts[ws] = cs
    ax.scatter(np.arange(1,54), counts, marker=markers[i], s=75, label=state, c=c[i],
               zorder=i+1)
ax.set_title("1986-2012 Percentage of Years with\n 1+ Tornado Warning for the Week of Year")
ax.set_ylabel("March Total")
ax.set_xlim(0, 53)
ax.set_yticks([0,10,25,50,75,90,100])
ax.set_ylim(-2, 101)
ax.set_ylabel("Percentage of Years")
ax.set_xticks( np.arange(1,56,7) )
ax.set_xticklabels( ('Jan 1', 'Feb 19', 'Apr 8', 'May 27', 'Jul 15', 'Sep 2', 'Oct 21', 'Dec 9'))

ax.grid(True)
ax.legend()

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
