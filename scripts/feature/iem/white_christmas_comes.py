import iemdb
import numpy as np
import mx.DateTime
import datetime
COOP = iemdb.connect('coop', bypass=True)

ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

# Get white christmases
ccursor.execute("""SELECT year from alldata_ia where sday = '1225' and
  snowd >= 1 and station = 'IA2203'""")

counts = np.zeros( (60,), 'f')

for row in ccursor:
    ccursor2.execute("""SELECT day, snowd from alldata_ia where
    station = 'IA2203' and sday < '1225' and year = %s ORDER by day DESC 
    LIMIT 60""", (row[0],))
    count = -2
    counts[-1] += 1
    for row2 in ccursor2:
        if row2[1] >= 1:
            counts[count] += 1
            count -= 1
        else:
            break
    #print row[0], count

counts2 = np.zeros((60,), 'f') 
for i in range(-1,-61,-1):
    ts = datetime.datetime(2000,12,25) + datetime.timedelta(days=i)
    ccursor.execute("""WITH obs as (
       SELECT year, snowd from alldata_ia where
       station = 'IA2203' and sday = %s),
      mins as (SELECT year, min(snowd) from alldata_ia 
       where station = 'IA2203' and sday >= %s and sday < '1225'
       GROUP by year),
      combo as (SELECT m.year, m.min, o.snowd from obs o JOIN mins m
      on (m.year = o.year) )

      SELECT sum(case when snowd >= 1 then 1 else 0 end),
      sum( case when snowd >= 1 and min >= 1 then 1 else 0 end) from combo
     """, (ts.strftime("%m%d"), ts.strftime("%m%d")))  
    row =  ccursor.fetchone()
    if row[0] > 0:
      counts2[i] = float(row[1]) / float(row[0]) * 100.

 
ets = mx.DateTime.DateTime(2000, 12, 25)
sts = ets - mx.DateTime.RelativeDateTime(days=60)
xticks = []
xticklabels = []
for i in range(2,60,3):
    ts = sts + mx.DateTime.RelativeDateTime(days=i+1)
    xticks.append( i )

    xticklabels.append( ts.strftime("%-d\n%b"))

import matplotlib.pyplot as plt



(fig, ax) = plt.subplots(1, 1)

ax.bar(np.arange(60)-0.3, counts / counts[-1] * 100.0, width=0.3,
       fc='b', ec='b', label='Snowcover on 12/25 Arrival')
ax.bar(np.arange(60), counts2, width=0.3, fc='r', ec='r',
       label='Snowcover Survived until 12/25')
ax.set_xticks( xticks )
ax.set_xticklabels( xticklabels )
ax.set_xlim(28,60)
ax.set_ylim(0, 100)
ax.set_yticks( [0,25,50,75,100])
ax.grid(True)
ax.set_ylabel("Frequency [%]")
ax.set_title("Des Moines 1895-2013 White Christmas")
ax.legend(loc=2)

fig.savefig('test.png')
