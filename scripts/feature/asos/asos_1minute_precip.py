import psycopg2
import datetime
import numpy
import pytz
ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor()
#acursor.execute("SET TIME ZONE 'EDT6EST'")
stemps = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
sprec = numpy.zeros( (3000,), 'f')

acursor.execute("""
 SELECT valid, tmpf, dwpf, drct, 
  sknt, pres1, gust_sknt, precip from t2014_1minute WHERE station = 'LWD'
 and valid BETWEEN '2014-06-03 00:00' and '2014-06-03 23:59' 
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
basets = datetime.datetime(2014,6,3)
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
sts = datetime.datetime(2014,6,3, 17, 0)
sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = sts + datetime.timedelta(minutes=421)
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
print xticks
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
x0 = 1168
ax.text(sts + datetime.timedelta(minutes=5), 10.85, "Minute Accums [inch]", va='bottom')
for i in range(x0,x0+11):
    ax.text( sts + datetime.timedelta(minutes=5), 10.65 + (x0-i)*0.69, "%s %.2f" % (
                                svalid[i].strftime("%-I:%M %p"), sprec[i],),
             va='top')
ax.set_xticks(xticks)
ax.set_ylabel("Precipitation [inch or inch/hour]")
ax.set_xticklabels(xlabels2)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.legend(loc=1, prop=prop, ncol=1)
ax.set_ylim(0,12)
ax.set_xlabel("3 June 2014 (CDT)")
ax.set_title("3 June 2014 Lamoni (KLWD) One Minute Rainfall\n5.27 inches total")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
