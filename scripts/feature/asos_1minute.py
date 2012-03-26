import iemdb
import mx.DateTime
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
#acursor.execute("SET TIME ZONE 'EDT5EST'")
stemps = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
valid = []
sprec = numpy.zeros( (1500,), 'f')
svalid = numpy.zeros( (1500,), 'f')

acursor.execute("""
 SELECT extract(epoch from (valid at time zone 'CDT')), tmpf, dwpf, drct, sknt, pres1, gust_sknt, precip,
  valid at time zone 'CDT' from t2012_1minute WHERE station = 'RST'
 and valid BETWEEN '2012-03-17 00:00' and '2012-03-19 00:00' 
and drct >= 0 ORDER by valid ASC
""")
for row in acursor:
        stemps.append( row[1])
        valid.append( row[0] )
        sdrct.append( row[3])
        ssknt.append( row[4] * 1.15)
        sdwpf.append( row[2] )
        pres1.append( row[5] )
        #sgust.append( row[6] * 1.15)
        #offset = row[8].hour * 60 + row[8].minute
        #if row[8].day == 8:
        #    offset += 1440
        #sprec[offset] = float(row[7] or 0) 


# Figure out ticks
sts = mx.DateTime.DateTime(2012,3,17, 0)
ets = mx.DateTime.DateTime(2012,3,19, 0)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
xticks = []
xlabels = []
while now <= ets:
    fmt = "%-I %p"
    if now == sts or now.hour == 0:
        fmt = "%-I %p\n%-d %B"
    
    if now == sts or (now.minute == 0 and now.hour % 6 == 0 ):
        xticks.append( int(now) )
        xlabels.append( now.strftime(fmt))
    now += interval

import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

fig = plt.figure()


ax = fig.add_subplot(111)
ax.plot(valid, stemps, color='r')
ax.plot([int(mx.DateTime.DateTime(2012,3,17,0,0)), 
	int(mx.DateTime.DateTime(2012,3,18,0,0))], [66,66], color='k')
ax.plot([int(mx.DateTime.DateTime(2012,3,18,0,0)), 
	int(mx.DateTime.DateTime(2012,3,19,0,0))], [60,60], color='k')
ax.text(int(mx.DateTime.DateTime(2012,3,18,0,0)), 59, "Previous High Temp Record of 60$^{\circ}\mathrm{F}$\nSet in 2010 [Archive: 1886-2011]", va='top')
ax.set_xticks(xticks)
ax.set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax.set_xticklabels(xlabels)
ax.grid(True)
#ax.set_xlim(min(xticks), max(svalid))
ax.legend(loc=2, prop=prop)
#ax.set_ylim(0,10)
#ax.set_xlabel("7 September 2011 (EDT)")
ax.set_title("Rochester, MN (KRST) One Minute Timeseries\n18 March 2012 Low Temperature was warmer than Record High!")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
