import matplotlib.pyplot as plt
fig = plt.figure()


from pyIEM import iemdb, mesonet
i = iemdb.iemdb()
asos = i['asos']
import mx.DateTime
import numpy
import numpy.ma

jdays = []
hours = []
vals = []
data = {}
maxV = 0
minV = 10000
for yr in range(1928,2011):
    rs = asos.query("""SELECT valid, tmpf, dwpf from t%s 
        WHERE station = 'DSM' and tmpf > 0 and dwpf > 0
        ORDER by valid ASC""" % (yr,)).dictresult()
    for i in range(len(rs)):
        ts = mx.DateTime.strptime(rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
        #key = ts.strftime("%Y%m%d%H")
        key = ts.strftime("%Y%m%d")
        #if data.has_key(key):
        #    continue
        #data[key] = 0
        h = rs[i]['dwpf']
        #h = mesonet.heatidx(rs[i]['tmpf'], mesonet.relh(rs[i]['tmpf'], rs[i]['dwpf']))
        if h >= maxV and rs[i]['tmpf'] >= 99:
            print h,  ts, rs[i]['tmpf'], rs[i]['dwpf']
            maxV = h
        #if ts.hour < 2:
        #    maxV = 0
        if h >= 100:
            data[key] = 0
            jdays.append( int(ts.strftime("%j")) )
            hours.append( ts.hour * 60 + ts.minute )
            vals.append( h )
        if h >= 100 and ts.hour > 5 and (ts.hour * 60 + ts.minute) <= minV:
            #print h, ts
            minV = (ts.hour * 60 + ts.minute)

sys.exit()
sts = mx.DateTime.DateTime(1949,1,1)
ets = mx.DateTime.DateTime(2011,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
running = 0
maxRunning = 0
while now < ets:
  if not data.has_key(now.strftime("%Y%m%d")):
    if running >= maxRunning or running > 4:
      print running, now
      maxRunning = running
    running = 0
  else:
    running += 1

  now += interval

xticks = []
xticklabels = []
for i in range(min(jdays)-5,max(jdays)+5):
    ts = mx.DateTime.DateTime(2000,1,1) + mx.DateTime.RelativeDateTime(days=i)
    if ts.day == 1 or ts.day == 15:
        xticks.append( i )
        xticklabels.append( ts.strftime("%b %-d"))

jdays = numpy.array(jdays)
hours = numpy.array(hours)
H, xedges, yedges = numpy.histogram2d(jdays, hours, bins=(53, 24),range=[[0,366],[0,1440]])
H = numpy.ma.array(H.transpose() / 63.)
H.mask = numpy.where( H < (1./63.), True, False)
extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
ax = fig.add_subplot(111)
res = ax.imshow(H,  extent=extent, aspect='auto', interpolation='nearest')
clr = fig.colorbar(res)
clr.ax.set_ylabel("Obs/year")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(min(jdays)-14,max(jdays)+14)

yticks = []
yticklabels = []
for i in range(min(hours),max(hours)):
    ts = mx.DateTime.DateTime(2000,1,1,0,0) + mx.DateTime.RelativeDateTime(minutes=i)
    if ts.minute == 0:
        yticks.append( i)
        yticklabels.append( ts.strftime("%I %p"))
ax.set_ylim(min(hours), max(hours))
ax.set_yticks( yticks ) 
ax.set_yticklabels( yticklabels )
ax.set_title("Des Moines 100+ $^{\circ}\mathrm{F}$ Heat Index Frequency [1948-2010]")
"""
ax = fig.add_subplot(211)
ax.set_title("Des Moines Days of 100+ Degree Heat Index [1948-2010]")
ax.scatter(jdays, vals)
ax.set_xlim(min(jdays)-5,max(jdays)+5)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels)
ax.grid(True)
ax.set_ylabel("Heat Index")


ax2 = fig.add_subplot(212)
ax2.scatter(jdays, hours)
ax2.set_xlim(min(jdays)-5,max(jdays)+5)
ax2.set_xticks(xticks)
ax2.set_xticklabels(xticklabels)
ax2.set_yticks(yticks)
ax2.set_yticklabels(yticklabels)
ax2.set_ylabel("Time of 100+ Degree Obs")
ax2.grid(True)
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')

