import iemdb
import mx.DateTime
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

stemps = []
svalid = []
sdrct = []
temps = []
valid = []
drct = []

acursor.execute("""
 SELECT extract(epoch from valid), tmpf, drct from alldata where station = 'AMW'
and valid between '2011-04-15' and '2011-05-16' and drct >= 0 ORDER by valid ASC
""")
for row in acursor:
    if row[2] > 179 and row[2] < 270:
        stemps.append( row[1])
        svalid.append( row[0])
        sdrct.append( row[2])
    else:
        temps.append( row[1])
        valid.append( row[0])
        drct.append( row[2])

# Figure out ticks
sts = mx.DateTime.DateTime(2011,4,15)
ets = mx.DateTime.DateTime(2011,5,16)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts
xticks = []
xlabels = []
while now <= ets:
    fmt = "%-d"
    if now == sts or now.day == 1:
        fmt = "%-d\n%B"
    
    if now == sts or now.day == 1 or now.day % 2 == 0:
        xticks.append( int(now) )
        xlabels.append( now.strftime(fmt))
    now += interval

import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(211)
ax.set_title("Ames Wind Direction & Air Temperature\n15 April - 15 May 2011")
ax.scatter(valid, drct)
ax.scatter(svalid, sdrct, color='r')
ax.set_xticks(xticks)
ax.set_xticklabels(xlabels)
ax.grid(True)
ax.set_xlim(min(xticks), max(xticks))
ax.set_ylim(0,361)
ax.set_yticks((0,90,180,270,360))
ax.set_yticklabels(('North','East','South','West','North'))

ax2 = fig.add_subplot(212)
ax2.scatter(valid, temps)
ax2.scatter(svalid, stemps, color='r')
ax2.set_xticks(xticks)
ax2.set_xticklabels(xlabels)
ax2.grid(True)
ax2.set_xlim(min(xticks), max(xticks))
ax2.set_ylabel("Air Temperature [F]")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
