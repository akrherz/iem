import iemdb
import mx.DateTime
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

stemps = []
svalid = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
sprec = numpy.zeros( (1440,), 'f')

acursor.execute("""
 SELECT extract(epoch from valid), tmpf, dwpf, drct, sknt, pres1, gust_sknt, precip, valid from t2011_1minute WHERE station = 'ORD'
 and valid BETWEEN '2011-07-23 00:00' and '2011-07-23 23:59' 
and drct >= 0 ORDER by valid ASC
""")
for row in acursor:
    
        stemps.append( row[1])
        svalid.append( row[0])
        sdrct.append( row[3])
        ssknt.append( row[4] )
        sdwpf.append( row[2] )
        pres1.append( row[5] )
        sgust.append( row[6] )
        offset = row[8].hour * 60 + row[8].minute
        sprec[offset] = float(row[7]) 

sprec = numpy.array( sprec )
acc = numpy.zeros( (1440,), 'f')
rate15 = numpy.zeros( (1440,), 'f')
rate60 = numpy.zeros( (1440,), 'f')
for i in range(1440):
    acc[i] = acc[i-1] + sprec[i]
    rate15[i] = numpy.sum(sprec[i-15:i]) * 4
    rate60[i] = numpy.sum(sprec[i-60:i])
print acc[:60]
# Figure out ticks
sts = mx.DateTime.DateTime(2011,7,23, 0)
ets = mx.DateTime.DateTime(2011,7,24, 0)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
xticks = []
xlabels = []
xlabels2 = []
while now <= ets:
    fmt = "%-I %p"
    if now == sts or now.hour == 0:
        fmt = "%-I %p\n%-d %B"
    
    if now == sts or now.minute == 0 or now.day % 2 == 0:
        xticks.append( int(now) )
        xlabels.append( now.strftime(fmt))
        xlabels2.append( now.strftime("%-I %p"))
    now += interval

import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

fig = plt.figure()

ax = fig.add_subplot(111)
ax.plot(svalid, acc, color='b', label="Accumulation")
ax.plot(svalid, sprec * 60, color='black', label="Hourly Rate over 1min")
ax.plot(svalid, rate15, color='g', label="Hourly Rate over 15min", linewidth=2)
ax.plot(svalid, rate60, color='r', label="Actual Hourly Rate")
ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks)-60*18*60)
ax.legend(loc=7, prop=prop)
#ax.set_ylim(0,10)
ax.set_xlabel("Morning of 23 July 2011")
ax.set_title("23 Jul 2011 Chicago O'Hare (KORD) One Minute Rainfall\nSet Local Daily Record of 6.86 inches")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))

"""
fig = plt.figure(figsize=(7.0,9.3))
ax = fig.add_subplot(411)
ax.set_title("Emporia (KEMP) ASOS One Minute Data [9-10 June 2011]")
ax.scatter(svalid, sdrct, color='b')
ax.set_xticks(xticks)
ax.set_ylabel("Wind Direction")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.set_ylim(0,361)
ax.set_yticks((0,90,180,270,360))
ax.set_yticklabels(('North','East','South','West','North'))


ax = fig.add_subplot(412)
ax.plot(svalid, ssknt, color='b', label="Speed")
ax.plot(svalid, sgust, color='r', label="Gust")
ax.set_xticks(xticks)
ax.set_ylabel("Wind Speed [kts]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.set_ylim(0,65)
ax.legend()
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))


ax2 = fig.add_subplot(413)
#ax2.scatter(valid, temps)
ax2.plot(svalid, stemps, color='r', label="Temperature")
ax2.plot(svalid, sdwpf, color='b', label="Dew Point")
ax2.set_xticks(xticks)
ax2.set_xticklabels(xlabels2)
ax2.grid(True)
ax2.legend(loc=4, prop=prop)
ax2.set_xlim(min(xticks), max(xticks))
ax2.set_ylim(30,100)
ax2.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
#ax2.set_xlabel("CDT")

ax3 = fig.add_subplot(414)
#ax2.scatter(valid, temps)
ax3.plot(svalid, pres1, color='r')
#ax3.plot(svalid, sdwpf, color='b', label="Dew Point")
ax3.set_xticks(xticks)
ax3.set_xticklabels(xlabels)
ax3.grid(True)
ax3.set_xlim(min(xticks), max(xticks))
ax3.set_ylabel("Pressure [inches]")
#ax3.set_xlabel("CDT")
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
