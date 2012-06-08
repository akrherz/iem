import matplotlib.pyplot as plt
import mx.DateTime
import matplotlib.patches as mpatches
from pyIEM import mesonet
import numpy

valid = []
pres = []
sped = []
drct = []
tmpf = []
dwpf = []
pday = []
lines = []
now = mx.DateTime.DateTime(2012,5,3,0,0)
txt2drct = {
 'N': '360',
 'North': '360',
 'NNE': '25',
 'NE': '45',
 'ENE': '70',
 'E': '90',
 'East': '90',
 'ESE': '115',
 'SE': '135',
 'SSE': '155',
 'S': '180',
 'South': '180',
 'SSW': '205',
 'SW': '225',
 'WSW': '250',
 'W': '270',
 'West': '270',
 'WNW': '295',
 'NW': '315',
 'NNW': '335'}

for line in open('bussey.txt'):
  if line.find("Min") > 0 or line.find("Max") > 0:
    continue
  ts = mx.DateTime.strptime(line[7:21], '%H:%M %m/%d/%y')
  if len(lines) == 0:
    now = ts
  if ts == now:
    lines.append( line )
    continue
  # Spread obs
  now = ts
  delta = 60.0 / len(lines)
  for line in lines:
    ts += mx.DateTime.RelativeDateTime(seconds=delta)
    t = float(line[42:45])
    rh = float(line[47:50])
    tmpf.append( t - 4 )
    dwpf.append( mesonet.dwpf(t -4,rh) )
    pres.append( float(line[52:57]) * 33.86375)
    sped.append( float(line[26:28]))
    pday.append( float(line[59:64]))
    drct.append( float(txt2drct[line[22:25].strip()]) - 20.0)
    valid.append( ts.ticks() )
  lines = []

sts = mx.DateTime.DateTime(2012,5,3,7,30)
ets = mx.DateTime.DateTime(2012,5,3,9,16)
interval = mx.DateTime.RelativeDateTime(minutes=15)
xticks = []
xticklabels = []
now = sts
while now < ets:
  fmt = ":%M"
  if now.minute == 0 or len(xticks) == 0:
    fmt = "%-I:%M %p"
  xticks.append( now.ticks() )
  xticklabels.append( now.strftime(fmt) )

  now += interval

fig, ax = plt.subplots(3,1, sharex=True)

fancybox = mpatches.FancyBboxPatch(
        [mx.DateTime.DateTime(2012,5,3,8,6).ticks(),
         40], 60*18, 50,
        boxstyle='round', alpha=0.2, facecolor='#7EE5DE', edgecolor='#EEEEEE', zorder=1)
ax[0].add_patch( fancybox)
ax[0].plot(valid, numpy.array(tmpf) , label='Air')
ax[0].plot(valid, numpy.array(dwpf), color='g' , label='Dew Point')
ax[0].set_ylim(40,90)
fancybox = mpatches.FancyBboxPatch(
        [mx.DateTime.DateTime(2012,5,3,8,6).ticks(),
         0], 60*18, 360,
        boxstyle='round', alpha=0.2, facecolor='#7EE5DE', edgecolor='#EEEEEE', zorder=1)
ax[1].add_patch( fancybox)
ax[1].scatter(valid, drct, zorder=2)
ax2 = ax[1].twinx()
ax2.plot(valid, sped, 'r')
ax2.set_ylabel("Wind Speed [mph]")

fancybox = mpatches.FancyBboxPatch(
        [mx.DateTime.DateTime(2012,5,3,8,6).ticks(),
         1000], 60*18, 1006,
        boxstyle='round', alpha=0.2, facecolor='#7EE5DE', edgecolor='#EEEEEE', 
zorder=1)
ax[2].add_patch( fancybox)
ax[2].plot(valid, pres, 'b', label="Pressure [mb]")
ax[2].set_ylim(1000,1006)
#ax3 = ax[2].twinx()
#ax3.plot(valid, pday, 'r')
#ax3.set_ylabel("Daily Precip [inch]")

ax[0].set_xticks( xticks )
ax[0].set_xticklabels( xticklabels )
ax[0].set_xlim( sts.ticks(), ets.ticks() )
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

ax[0].legend(loc=1, prop=prop, ncol=2)
ax[2].legend(loc=1, prop=prop)
ax[0].grid(True)
ax[1].grid(True)
ax[2].grid(True)
ax[0].set_title("Bussey - Twin Cedars SchoolNet8 Site (~ $\Delta$6 second data)")
ax[2].set_xlabel("Morning of 3 May 2012, * -4$^{\circ}\mathrm{F}$ temp correction applied")
#ax[2].set_ylabel("Pressure [mb]")
#[t.set_color('red') for t in ax3.yaxis.get_ticklines()]
#[t.set_color('red') for t in ax3.yaxis.get_ticklabels()]
[t.set_color('red') for t in ax2.yaxis.get_ticklines()]
[t.set_color('red') for t in ax2.yaxis.get_ticklabels()]
[t.set_color('b') for t in ax[2].yaxis.get_ticklines()]
[t.set_color('b') for t in ax[2].yaxis.get_ticklabels()]
[t.set_color('b') for t in ax[0].yaxis.get_ticklines()]
[t.set_color('b') for t in ax[0].yaxis.get_ticklabels()]
[t.set_color('b') for t in ax[1].yaxis.get_ticklines()]
[t.set_color('b') for t in ax[1].yaxis.get_ticklabels()]
ax[1].set_ylabel("Wind Direction")
ax[0].set_ylabel("Temperature $^{\circ}\mathrm{F}$")
ax[1].set_yticks( numpy.arange(0,361,90) )
ax[1].set_ylim(0,361)
ax[1].set_yticklabels( ['N','E','S','W','N'] )
ax[2].set_yticks( numpy.arange(1000,1007) )
ax[2].set_yticklabels( numpy.arange(1000,1007) )
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
