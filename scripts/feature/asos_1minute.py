import iemdb
import mx.DateTime
import numpy
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()
#acursor.execute("SET TIME ZONE 'CDT6CST'")
stemps = []
sdrct = []
ssknt = []
sdwpf = []
pres1 = []
sgust = []
svalid = []
sprec = []

acursor.execute("""
 SELECT extract(epoch from (valid at time zone 'CDT')), tmpf, dwpf,
 drct, sknt, pres1, gust_sknt, precip,
  valid at time zone 'CDT' from t2012_1minute WHERE station = 'SGF'
 and valid BETWEEN '2012-04-25 00:00-05' and '2012-04-25 23:59-05' 
 ORDER by valid ASC
""")
for row in acursor:
        stemps.append( row[1])
        
        sdrct.append( float(row[3] or 0))
        ssknt.append( (row[4] or 0) * 1.15)
        sdwpf.append( row[2] )
        pres1.append( row[5] )
        sgust.append( (row[6] or 0) * 1.15)
        sprec.append( float(row[7] or 0) )
        svalid.append( row[0] )
 
print sgust

sts = mx.DateTime.DateTime(2012,4,25, 0,0)
ets = mx.DateTime.DateTime(2012,4,25, 6,1)
interval = mx.DateTime.RelativeDateTime(hours=1)
now = sts
xticks = []
xlabels = []
while now <= ets:
    fmt = "%-I %p"
    if now == sts or now.hour == 0:
        fmt = "%-I %p\n%-d %B"
    
    if now == sts or (now.minute == 0 and now.hour % 1 == 0 ):
        xticks.append( int(now) )
        xlabels.append( now.strftime(fmt))
    now += interval

import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

#fig = plt.figure()
#fig = plt.figure(figsize=(7.0,9.3))
fig, axes = plt.subplots(3,1, sharex=True, figsize=(7.0,9.3))

axes[0].plot(svalid, stemps, color='r', label="Temperature")
axes[0].plot(svalid, sdwpf, color='b', label="Dew Point")
axes[0].set_xticks(xticks)
axes[0].set_ylabel("Temperature [F]")
axes[0].set_xticklabels(xlabels)
axes[0].grid(True)
axes[0].set_xlim(min(xticks), max(xticks))
axes[0].legend(loc=2, prop=prop)
#ax.set_ylim(0,10)
axes[0].set_title("25 Apr 2012 Springfield, MO (KSGF) One Minute Time Series")
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))

axes[1].scatter(svalid, sdrct, color='k')
axes[1].set_xticks(xticks)
axes[1].set_ylabel("Wind Direction")
axes[1].set_xticklabels(xlabels)
axes[1].grid(True)
axes[1].set_xlim(min(xticks), max(xticks))
axes[1].set_ylim(0,361)
axes[1].set_yticks((0,90,180,270,360))
axes[1].set_yticklabels(('North','East','South','West','North'))

ax2 = axes[1].twinx()
ax2.plot(svalid, ssknt, color='b', label='Speed')
ax2.plot(svalid, sgust, color='r', label='Gust')
ax2.set_ylabel("Wind Speed [mph]")
ax2.legend(loc=2, prop=prop)


axes[2].plot(svalid, pres1, color='k')
axes[2].set_xticks(xticks)
axes[2].set_ylabel("Pressure Altimeter [in]")
axes[2].set_xticklabels(xlabels)
axes[2].grid(True)
axes[2].set_xlim(min(xticks), max(xticks))
axes[2].legend(loc=3,ncol=2)
#ax.set_ylim(0,361)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))
"""

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
