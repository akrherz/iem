import psycopg2
import datetime
import numpy as np
import mx.DateTime
COOP = psycopg2.connect(database='coop', host='iemdb', user='nobody')
cursor = COOP.cursor()

dates = []
ends = []
labels = []
for thres in range(0,-31,-1):
    cursor.execute("""
    SELECT max(day) - 'today'::date, max(day) from alldata_ia where station = 'IA2203'
    and low <= %s
    """, (thres,))
    row = cursor.fetchone()
    dates.append(row[0])
    ends.append( datetime.datetime.today() )
    ts = mx.DateTime.DateTime(row[1].year, row[1].month, row[1].day)
    labels.append(ts.strftime("%-d %b %Y"))
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

bars = ax.barh(np.arange(0,-31,-1)-0.4, dates, left=ends)
for i, bar in enumerate(bars):
    ax.text(bar.get_x() - 201, bar.get_y(), labels[i], ha='right', fontsize=10)
ax.set_ylim(-30.5,0.5)
xticks = []
xticklabels = []
for yr in range(1880,2013,25):
    ts = datetime.date(yr, 1,1)
    xticks.append( ts )
    xticklabels.append( yr )

ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_xlim(datetime.date(1860,1,1),datetime.date(2014,1,1))
ax.grid(True)
ax.set_ylabel("Temperature At Or Below $^\circ$F")
ax.set_xlabel("Last Event up to and including 23 Dec 2013")
ax.set_title("Des Moines Period since as Cold Low Temperature")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')