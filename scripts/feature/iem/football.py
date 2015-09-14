import psycopg2
import datetime

data = """2002-09-14 17:05 S
2003-09-13 11:30 I
2004-09-11 11:05 I
2005-09-10 14:30 S
2006-09-16 11:00 I
2007-09-15 12:30 S
2008-09-13 11:00 I
2009-09-12 11:00 I
2010-09-11 14:30 I
2011-09-10 11:00 S
2012-09-08 14:42 S
2013-09-14 17:00 I
2014-09-13 15:30 S
2015-09-12 15:45 I"""

pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = pgconn.cursor()

years = []
tmpf = []
sknt = []
colors = []
for line in data.split("\n"):
    ts = datetime.datetime.strptime(line.strip()[:16], '%Y-%m-%d %H:%M')
    sts = ts - datetime.timedelta(hours=1)
    ets = ts + datetime.timedelta(minutes=30)
    station = 'AMW' if ts.year % 2 == 1 else 'IOW'
    cursor.execute("""
    SELECT tmpf, sknt from alldata where station = %s
    and valid between %s and %s ORDER by valid DESC
    """, (station, sts, ets))
    row = cursor.fetchone()
    print ts, station, row
    years.append(ts.year)
    tmpf.append(row[0])
    sknt.append(row[1] * 1.15)
    colors.append('k' if line[-1] == 'I' else '#A71930')

import matplotlib.pyplot as plt
import numpy as np

(fig, ax) = plt.subplots(1, 1)
bars = ax.barh(np.array(years) - 0.4, tmpf)
irec = None
srec = None
for i, bar in enumerate(bars):
  bar.set_facecolor(colors[i])
  if colors[i] == 'k':
    irec= bar
  else:
    srec = bar
  ax.text(tmpf[i]+1, years[i], '%.0f' % (tmpf[i],), va='center')
n90 = [100]*len(years)
bars = ax.barh(np.array(years) - 0.4, sknt, left=n90)
for i, bar in enumerate(bars):
  bar.set_facecolor(colors[i])
  ax.text(sknt[i]+101, years[i], '%.0f' % (sknt[i],), va='center')
ax.set_xticks([55, 60, 65, 70, 75, 80, 85, 90, 100, 105, 110, 115, 120])
ax.set_xticklabels([55, 60, 65, 70, 75, 80, 85, 90, 0, 5, 10, 15, 20])
ax.set_xlabel("Air Temperature [F]                          Wind Speed [mph]")
ax.set_xlim(55, 125)
ax.grid(True)
ax.set_title("2002-2015 Iowa State vs Iowa Football Kickoff Weather\nClosest Ob in Time, Ames (AMW) or Iowa City (IOW)")
ax.legend((irec, srec), ('Iowa Won', 'Iowa State Won'), ncol=2)
ax.set_ylim(2001.5, 2017.5)

fig.savefig('test.png')


