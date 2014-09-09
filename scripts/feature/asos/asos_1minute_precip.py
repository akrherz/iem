import psycopg2
import datetime
import numpy
import pytz
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()
acursor.execute("SET TIME ZONE 'MDT8MST'")
stemps = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
sprec = numpy.zeros( (3000,), 'f')

acursor.execute("""
 SELECT valid, tmpf, dwpf, drct, 
  sknt, pres1, gust_sknt, precip from t2014_1minute WHERE station = 'PHX'
 and valid BETWEEN '2014-09-08 00:00' and '2014-09-08 23:59' 
 ORDER by valid ASC
""")
tot = 0
for row in acursor:
    offset = row[0].hour * 60 + row[0].minute
    if row[0].day == 36:
        offset += 1440
    if row[7] > 0:
        if row[7] > 0.05:
            print offset, row[0], row[7]
        tot += row[7]
    sprec[offset] = float(row[7] or 0) 
        
print tot

acc = numpy.zeros( (3000,), 'f')
rate15 = numpy.zeros( (3000,), 'f')
rate60 = numpy.zeros( (3000,), 'f')
svalid = [0]*3000
basets = datetime.datetime(2014,9,8)
basets = basets.replace(tzinfo=pytz.timezone("America/Phoenix"))

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
sts = datetime.datetime(2014,9,8,1, 0)
sts = sts.replace(tzinfo=pytz.timezone("America/Phoenix"))
ets = sts + datetime.timedelta(minutes=8*60+1)
interval = datetime.timedelta(minutes=60)
now = sts
xticks = []
xlabels = []
xlabels2 = []
while now <= ets:
    fmt = "%-I %p"
    #if now == sts or now.hour == 0:
    #    fmt = "%-I %p\n%-d %B"
    
    #if now == sts or (now.minute == 0 and now.hour % 1 == 0 ):
    xticks.append( now )
    xlabels.append( now.strftime(fmt))
    xlabels2.append( now.strftime(fmt))
    now += interval
xlabels[-1] = 'Mid'

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
ax.plot(svalid, rate15, color='yellow', label="Hourly Rate over 15min", linewidth=3.5, zorder=3)
ax.plot(svalid, rate15, color='k', linewidth=1, zorder=4)
ax.plot(svalid, rate60, color='r', label="Actual Hourly Rate", lw=3.5,zorder=3)
ax.plot(svalid, rate60, color='k', lw=1, zorder=4)
x0 = 157
ax.text(sts + datetime.timedelta(seconds=330), 4.45, "Minute Accums [inch]", va='bottom')
for i in range(x0,x0+15):
    ax.text( sts + datetime.timedelta(seconds=330), 4.4 + (x0-i)*0.29, "%s %.2f" % (
                                svalid[i].strftime("%-I:%M %p"), sprec[i],),
             va='top')
ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.legend(loc=2, prop=prop, ncol=1)
ax.set_ylim(0,6)
ax.set_xlabel("8 September 2014 (Phoenix Local Time)")
ax.set_title("8 September 2014 Phoenix, AZ (KPHX) One Minute Rainfall")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))


fig.savefig('test.png')
#import iemplot
#iemplot.makefeature('test')
