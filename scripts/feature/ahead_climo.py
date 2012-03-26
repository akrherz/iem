import iemdb
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

climate = {}
ccursor.execute("""
  SELECT valid, high from climate51 where station = 'IA0200'
""")
for row in ccursor:
    climate[row[0].strftime("%m%d")] = row[1]

ccursor.execute("""
  SELECT day, high from alldata_ia where year = 2012 and station = 'IA0200'
  ORDER by day ASC
""")
doy = []
ahead = []
bdoy = []
behind = []
for row in ccursor:
    high = row[1]
    day = mx.DateTime.strptime(row[0].strftime("%Y%m%d"), "%Y%m%d")
    chigh = climate[day.strftime("%m%d")]
    if high < chigh:
        while climate[day.strftime("%m%d")] > high:
            if (day.day == 1 and day.month == 1):
                break
            day -= mx.DateTime.RelativeDateTime(days=1)
        behind.append( int(day.strftime("%j")))
        bdoy.append( int(row[0].strftime("%j")) )      
        print day, high, climate[day.strftime("%m%d")]
    else:
        while climate[day.strftime("%m%d")] < high:
            day += mx.DateTime.RelativeDateTime(days=1)
        ahead.append( int(day.strftime("%j")))
        doy.append( int(row[0].strftime("%j")) )
forecast = [62,75,78,75,73,72,71,71]
days = [12,13,14,15,16,17,18,19]
for row in zip(days, forecast):
    high = row[1]
    day = mx.DateTime.strptime("201203"+str(row[0]), "%Y%m%d")
    chigh = climate[day.strftime("%m%d")]
    if high < chigh:
        while climate[day.strftime("%m%d")] > high:
            if (day.day == 1 and day.month == 1):
                break
            day -= mx.DateTime.RelativeDateTime(days=1)
        behind.append( int(day.strftime("%j")))
        bdoy.append( int(mx.DateTime.strptime("201203"+str(row[0]), "%Y%m%d").strftime("%j")) )      
        print day, high, climate[day.strftime("%m%d")]
    else:
        while climate[day.strftime("%m%d")] < high:
            day += mx.DateTime.RelativeDateTime(days=1)
        ahead.append( int(day.strftime("%j")))
        doy.append( int(mx.DateTime.strptime("201203"+str(row[0]), "%Y%m%d").strftime("%j")) )

import numpy as np
ahead = np.array(ahead)
doy = np.array(doy)
behind = np.array(behind)
bdoy = np.array(bdoy)

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar(doy-0.4, ahead-doy, bottom=doy, fc='r', ec='r')
for bar in bars[-7:]:
    bar.set_facecolor('green')
    bar.set_edgecolor('green')
ax.bar(bdoy-0.4, bdoy-behind, bottom=behind, fc='b', ec='b')
sts = mx.DateTime.DateTime(2000,1,1)
ets = mx.DateTime.DateTime(2001,1,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
xticks = []
xticklabels = []
while now < ets:
  xticks.append( (now - sts).days )
  xticklabels.append( now.strftime("%b %-d") )
  now += interval
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.set_yticks(xticks)
ax.set_yticklabels(xticklabels)
ax.set_xlim(0,80)
ax.set_ylim(0,160)
ax.grid(True)
ax.set_ylabel("Feels like Date")
ax.set_xlabel("2012 Daily High Temperature (green is forecasted)")
ax.set_title("2012 Ames Daily High Feels like Climatology on...")
fig.savefig("test.ps")
import iemplot
iemplot.makefeature('test')