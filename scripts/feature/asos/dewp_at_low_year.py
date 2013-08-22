import psycopg2
import numpy as np
import datetime

dd = [0]*(2014-1935)
x = []
for i in range(len(dd)):
    dd[i] = []
    x.append( "%s" % (1935 + i,) if i % 5 == 0 else "" )

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()


acursor.execute("""
 SELECT extract(year from date), avg from
   (select date, avg(tmpf - dwpf) from 
     (select date(valid), tmpf, dwpf, 
      rank() over (PARTITION by date(valid) ORDER by tmpf ASC) from alldata
      where station = 'DSM' and valid > '1935-01-01' and dwpf > -50
      and tmpf < 100 and extract(month from valid) in (9,10,11)) as foo 
   WHERE rank = 1 and tmpf - dwpf < 40 GROUP by date) as foo2
""")

for row in acursor:
    week = int(row[0]) - 1935
    dd[week].append( row[1] )
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.set_title("1935-2013 Des Moines *SON* Dewpoint Depression at Daily Low")
ax.set_ylabel("Dewpoint Depression $^\circ$F")
ax.boxplot(dd)
ax.set_xticklabels(x, rotation=90)
ax.set_ylim(0,25)
ax.grid(True, axis='y')

fig.savefig('test.png')