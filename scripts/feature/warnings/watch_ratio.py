import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import psycopg2
import datetime

dbconn = psycopg2.connect(database='postgis', user='nobody', host='iemdb')
cursor = dbconn.cursor()

cursor.execute("""
  SELECT extract(week from issued) as d, sum(case when type = 'SVR' then 1 else 0 end), sum(case when type = 'TOR' then 1 else 0 end), count(*)
  from watches WHERE issued < '2013-01-01' GROUP by d ORDER by d ASC
""")

days = []
ratio = []
avgyr = []
for row in cursor:
    days.append( datetime.datetime(2000,1,1) + datetime.timedelta(days=7*(row[0]-1)) )
    ratio.append( float(row[1]) / float(row[2]))
    avgyr.append( row[3] / (2013-1997) / 7.0)
print days
ratio = np.array(ratio)
(fig, ax) = plt.subplots(1,1)
ax.bar(days, ratio, fc='green', ec='green', width=7)

ax2 = ax.twinx()
ax2.scatter(days, avgyr, s=75, marker='s', c='r')
ax2.set_ylabel("Avg Number of Total Watches per day (dots)", color='r')

ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.set_title("1997-2012 Storm Prediction Center Watches")
ax.set_ylabel("Ratio Severe Tstorm / Tornado Watches (bars)", color='green')
ax.set_xlim(days[0], days[-1])
ax2.set_ylim(bottom=0)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
