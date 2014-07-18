import psycopg2
import pandas as pd

PGCONN = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = PGCONN.cursor()

res = []

for i in range(1,32):
    cursor.execute("""
    WITH streaks as (SELECT day, month, 
    avg(low) OVER (ORDER by day ASC ROWS BETWEEN %s PRECEDING and CURRENT ROW) as l,
    avg(high) OVER (ORDER by day ASC ROWS BETWEEN %s PRECEDING and CURRENT ROW) as h
     from alldata_ia where station = 'IA2203')
     
     SELECT min(l), max(l), min(h), max(h) from streaks where month = 7 and extract(day from day) > %s
    
    """, (i,i,i-1))
    
    row = cursor.fetchone()
    
    print i, row
    res.append( dict(i=i, minl=row[0], maxl=row[1], minh=row[2], maxh=row[3]))
    
df = pd.DataFrame(res)

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.plot(range(1,32), df['minl'], label='Min Low', lw=2, c='b')
ax.plot(range(1,32), df['maxl'], '-.', label='Max Low', lw=2, c='b')

ax.plot(range(1,32), df['minh'], '-.', label='Min High', lw=2, c='r')
ax.plot(range(1,32), df['maxh'], label='Max High', lw=2, c='r')

ax.set_ylabel("Average Temperature $^\circ$F")
ax.set_xlabel("Consecutive Day Period within July")
ax.legend(ncol=4, loc=4, fontsize=12)
ax.grid(True)
ax.set_xlim(0.8, 31.2)
ax.set_title("1886-2013 Des Moines July Average Temperature Extremes\nfor streaks of days completely within July")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')