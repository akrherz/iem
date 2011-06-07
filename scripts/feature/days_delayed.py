import iemdb
import math
import mx.DateTime
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()

climate = {}
ccursor.execute("SELECT valid, high from ncdc_climate71 where station = 'ia0200'")
for row in ccursor:
    climate[ row[0].strftime("%m%d") ] = row[1]

minds = []
icursor.execute("SELECT day, max_tmpf from summary_2011 where station = 'AMW' and day >= '2011-01-20' and network = 'IA_ASOS' ORDER by day ASC")
for row in icursor:
    ts = mx.DateTime.strptime(row[0].strftime("%Y-%m-%d"), '%Y-%m-%d')
    jday = int(ts.strftime("%j"))
    high = row[1]
    minV = 100.
    minD = 0
    for i in range(180):
        for d in [i,-i]:
            ts0 = ts + mx.DateTime.RelativeDateTime(days=d)
            cli = climate[ ts0.strftime("%m%d")]
            if abs( cli - high ) < minV:
                
                minV =  abs( cli - high )
                j = int(ts0.strftime("%j"))
                if j > 180:
                    minD = j - (jday+366)
                else:
                    minD = j - jday
    print "Day: %s High: %s Search: %s" % (ts, high, minD)
    minds.append( minD )

xticks = []
xticklabels = []
sts = mx.DateTime.DateTime(2011,1,20)
ets = mx.DateTime.DateTime(2011,3,28)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
i = 0
while now < ets:
    if now.day in [1,8,15,22]:
        xticks.append(i)
        xticklabels.append(now.strftime("%-d %b"))
    i += 1
    now += interval


import matplotlib.pyplot as plt
import numpy

fig = plt.figure()
ax = fig.add_subplot(111)

bars = ax.bar( numpy.arange(0,len(minds)) - 0.3, minds)
for bar in bars:
    if bar.get_y() >= 0:
        bar.set_facecolor('r') 
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid(True)
ax.set_title("Ames Daily High Temperature Departure\n(number of days to match high with climatology)")
ax.set_ylabel("Days from climatology")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
    
    