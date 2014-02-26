import psycopg2
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

cursor.execute("""
WITH one as
 (SELECT extract(year from day + '5 months'::interval) as yr, sum(snow) 
 from alldata_ia where station = 'IA4735' GROUP by yr),
 
 two as 
 (SELECT extract(year from day + '5 months'::interval) as yr, sum(snow) 
 from alldata_ia where station = 'IA2364' GROUP by yr)

 SELECT one.yr, one.sum, two.sum from one JOIN two on (one.yr = two.yr)
 WHERE one.sum > 3 and two.sum > 3 ORDER by one.yr ASC

""")
years = []
x = []
y = []
for row in cursor:
    years.append( row[0] )
    x.append( row[1])
    y.append( row[2])
x[-1] = 13

import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)
ax.scatter(x, y)
ax.scatter(x[-1], y[-1], 40, marker='s', color='r')
for mx, my, myear in zip(x, y, years):
    if abs(mx - my) > 30:
        ax.text(mx, my+1, "%.0f" % (myear,), color='r')
         
ax.plot([0,90], [0,90])
ax.set_xlim(0,90)
ax.set_ylim(0,90)
ax.set_xticks(range(0,12*8,12))
ax.set_yticks(range(0,12*8,12))
ax.grid(True)
ax.set_title("Dubuque vs Le Mars Seasonal Snowfall [1941-2014]\n* 2014 thru 25 Feb")
ax.set_ylabel("Dubuque Snowfall [inch]")
ax.set_xlabel("Le Mars Snowfall [inch]")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')