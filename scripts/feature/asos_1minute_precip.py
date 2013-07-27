import psycopg2
import datetime
import numpy
import pytz
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()
#acursor.execute("SET TIME ZONE 'CDT6CST'")
stemps = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
sprec = numpy.zeros( (3000,), 'f')

acursor.execute("""
 SELECT valid, tmpf, dwpf, drct, 
  sknt, pres1, gust_sknt, precip from t2013_1minute WHERE station = 'OKC'
 and valid BETWEEN '2013-07-26 00:00' and '2013-07-26 23:59' 
 ORDER by valid ASC
""")
tot = 0
for row in acursor:
        offset = row[0].hour * 60 + row[0].minute
        if row[0].day == 36:
            offset += 1440
        if row[7] > 0:
            print offset, row[0], row[7]
            tot += row[7]
        sprec[offset] = float(row[7] or 0) 
        
print tot

acc = numpy.zeros( (3000,), 'f')
rate15 = numpy.zeros( (3000,), 'f')
rate60 = numpy.zeros( (3000,), 'f')
svalid = [0]*3000
basets = datetime.datetime(2013,7,26)
basets = basets.replace(tzinfo=pytz.timezone("America/Chicago"))
for i in range(3000):
    acc[i] = acc[i-1] + sprec[i]
    rate15[i] = numpy.sum(sprec[i-14:i+1]) * 4
    rate60[i] = numpy.sum(sprec[i-59:i+1])
    svalid[i] =  basets + datetime.timedelta(minutes=i)

#print acc[818:843]
#print rate60[818:912]
#for i in range(818,912):
#    print "%s,%.0f,%s" % (i, svalid[i], svalid[i])
#    print mx.DateTime.DateTime(2012,8,4, 0) + mx.DateTime.RelativeDateTime(minutes=i)

# Figure out ticks
sts = datetime.datetime(2013,7,26, 4, 0)
sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = sts + datetime.timedelta(minutes=121)
interval = datetime.timedelta(minutes=10)
now = sts
xticks = []
xlabels = []
xlabels2 = []
while now <= ets:
    fmt = "%-I:%M"
    #if now == sts or now.hour == 0:
    #    fmt = "%-I %p\n%-d %B"
    
    #if now == sts or (now.minute == 0 and now.hour % 1 == 0 ):
    xticks.append( now )
    xlabels.append( now.strftime(fmt))
    xlabels2.append( now.strftime(fmt))
    now += interval

import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

fig = plt.figure()


ax = fig.add_subplot(111)
print numpy.shape(svalid)
print numpy.shape(acc)
print numpy.max(rate60)
ax.bar(svalid, sprec * 60, width=1./1440., fc='b', ec='b', label="Hourly Rate over 1min",
       zorder=1)
ax.plot(svalid, acc, color='k', label="Accumulation",lw=2, zorder=2)
ax.plot(svalid, rate15, color='g', label="Hourly Rate over 15min", linewidth=2)
ax.plot(svalid, rate60, color='r', label="Actual Hourly Rate", lw=2)
ax.text(xticks[1], 14.6, "Minute Accumulations [inch]", va='bottom')
for i in range(308,320):
    ax.text( xticks[1], 14.5 + (308-i)*0.7, "%s %.2f" % (svalid[i].strftime("%-I:%M %p"), sprec[i],),
             va='top')
ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.legend(loc=2, prop=prop, ncol=1)
ax.set_ylim(0,20)
ax.set_xlabel("Morning of 26 July 2013 (CDT)")
ax.set_title("26 July 2013 Oklahoma City, OK (KOKC) One Minute Rainfall\n3.54 inches total")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))

"""
fig = plt.figure(figsize=(7.0,9.3))
ax = fig.add_subplot(311)
ax.set_title("Binghamton,NY (KBGM) ASOS [7 Sep 2011]")
ax.scatter(svalid, sdrct, color='b')
ax.set_xticks(xticks)
ax.set_ylabel("Wind Direction")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.set_ylim(0,361)
ax.set_yticks((0,90,180,270,360))
ax.set_yticklabels(('North','East','South','West','North'))


ax = fig.add_subplot(312)
ax.plot(svalid, ssknt, color='b', label="Speed")
ax.plot(svalid, sgust, color='r', label="Gust")
ax.set_xticks(xticks)
ax.set_ylabel("5 Second Wind Speed [mph]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.set_ylim(0,80)
ax.legend(loc=3,ncol=2)
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


ax3 = fig.add_subplot(313)
#ax2.scatter(valid, temps)
ax3.plot(svalid, pres1, color='r')
#ax3.plot(svalid, sdwpf, color='b', label="Dew Point")
ax3.set_xticks(xticks)
ax3.set_xticklabels(xlabels)
ax3.grid(True)
ax3.set_xlim(min(xticks), max(xticks))
ax3.set_ylabel("Pressure [inches]")
ax3.set_xlabel("EDT")
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
