import iemdb
import datetime
import numpy
import pytz
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
 SELECT valid, tmpf, dwpf,
 drct, sknt, pres1, gust_sknt, precip,
  valid at time zone 'CDT' from t2013_1minute WHERE station = 'GRI'
 and valid BETWEEN '2013-06-11 2:00' and '2013-06-11 7:59' 
 ORDER by valid ASC
""")
for row in acursor:
        stemps.append( row[1])
        
        sdrct.append( float(row[3] or 0))
        if row[4] > 60:
            ssknt.append( None )
        else:
            ssknt.append( (row[4] or 0) * 1.15)
        sdwpf.append( row[2] )
        pres1.append( row[5] )
        sgust.append( (row[6] or 0) * 1.15)
        sprec.append( float(row[7] or 0) )
        ts = row[0].replace(tzinfo=pytz.timezone('America/Chicago'))
        svalid.append( ts )
 
#print sgust

sts = datetime.datetime(2013,6,11, 2,0)
sts = sts.replace(tzinfo=pytz.timezone("America/Chicago"))
ets = datetime.datetime(2013,6,11, 8,1)
ets = ets.replace(tzinfo=pytz.timezone("America/Chicago"))
interval = datetime.timedelta(hours=1)
now = sts
xticks = []
xlabels = []
while now <= ets:
    print now
    fmt = "%-I %p"
    if now == sts or now.hour == 0:
        fmt = "%-I %p\n%-d %B"
    
    if now == sts or (now.minute == 0 and now.hour % 1 == 0 ):
        xticks.append( now )
        xlabels.append( now.strftime(fmt))
    now += interval
print xticks

import matplotlib.pyplot as plt
import matplotlib.font_manager 
prop = matplotlib.font_manager.FontProperties(size=12) 

#fig = plt.figure()
#fig = plt.figure(figsize=(7.0,9.3))
fig, axes = plt.subplots(2,1, sharex=True, figsize=(7.0,9.3))

axes[0].plot(svalid, stemps, color='r', label="Temperature")
axes[0].plot(svalid, sdwpf, color='b', label="Dew Point")
axes[0].set_xticks(xticks)
axes[0].set_ylabel("Temperature [F]")
axes[0].set_xticklabels(xlabels)
axes[0].grid(True)
axes[0].set_xlim(xticks[0], xticks[-1])
axes[0].legend(loc=2, prop=prop, ncol=1)
#ax.set_ylim(0,10)
axes[0].set_title("11 June 2013 Grand Island, NE (KGRI) One Minute Time Series")
axes[0].set_ylim(35,105)
#ax.set_yticks((0,90,180,270,360))
#ax.set_yticklabels(('North','East','South','West','North'))

axes[1].plot(svalid, sdrct, color='k', linestyle='None', marker='o')
axes[1].set_ylabel("Wind Direction")
axes[1].grid(True)
#axes[1].set_xlim(min(xticks), max(xticks))
axes[1].set_ylim(0,361)
axes[1].set_yticks((0,90,180,270,360))
axes[1].set_yticklabels(('North','East','South','West','North'))

ax2 = axes[1].twinx()
ax2.plot(svalid, ssknt, color='b', label='Speed')
#ax2.plot(svalid, sgust, color='r', label='Gust')
ax2.set_ylabel("Wind Speed [mph]")
ax2.legend(loc=2, prop=prop)

#axes[2].plot(svalid, pres1, color='k')
#axes[2].set_xticks(xticks)
#axes[2].set_ylabel("Pressure Altimeter [in]")
#axes[2].set_xticklabels(xlabels)
#axes[2].grid(True)
#axes[2].set_xlim(min(xticks), max(xticks))

"""
axes[2].set_xlim(xticks[0], xticks[-1])
axes[2].legend(loc=3,ncol=1)
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
fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
