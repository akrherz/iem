import psycopg2
import numpy as np
import datetime

COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

highs = []
doy = []
years = []

cursor.execute("""
  SELECT day, high, sday, rank from 
  (SELECT day, high, sday, 
  rank() over (partition by high ORDER by sday DESC)
  from alldata_ia WHERE
  station = 'IA2203') as foo
  WHERE rank = 1 ORDER by high DESC""")

jan1 = datetime.datetime(2000,1,1)
last = 0
for row in cursor:
    ts = datetime.datetime(2000, int(row[2][:2]),int(row[2][2:]))
    days = (ts-jan1).days + 1
    if days < last:
        days = last
        years.append( None )
    else:
        years.append(row[0].year)
    last = days
    doy.append( days )
    highs.append( row[1] )
    
import matplotlib.pyplot as plt
highs = np.array(highs)
(fig, ax) = plt.subplots(1,1)

bars = ax.barh(highs-0.4, doy, fc='r', ec='r')
for i, bar in enumerate(bars):
    if years[i] is not None and highs[i] > 65:
        ax.text(doy[i], highs[i], "%s" % (years[i],), ha='left', va='center')
    if years[i] == 2013:
        bar.set_facecolor('g')
        bar.set_edgecolor('g')
        bars[i+2].set_facecolor('g')
        bars[i+2].set_edgecolor('g')
        bars[i+3].set_facecolor('g')
        bars[i+3].set_edgecolor('g')
ax.set_ylim(64.5,110.5)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(200,366)
ax.grid(True)
ax.set_title("1880-2013 Des Moines Latest Date for High Temperature")
ax.set_ylabel("High Temperature $^\circ$F")
ax.set_xlabel("*2013 data thru 2 September")

fig.savefig('test.png')
