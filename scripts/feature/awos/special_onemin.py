import matplotlib.pyplot as plt
import datetime
import pytz
import numpy as np
from pyiem.datatypes import temperature, speed
import matplotlib.dates as mdates

valid = []
tmpc = []
dwpc = []
sknt = []
drct = []
gust = []
alti = []
for line in open('/tmp/KOXV_JUL2313.TXT'):
    if line[:4] != "KOXV":
        continue
    ddhhmm = line[5:11]
    ts = datetime.datetime(2013,7,23,int(ddhhmm[2:4]), int(ddhhmm[4:]))
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    valid.append( ts.astimezone(pytz.timezone("America/Chicago")))

    tmpc.append( float(line[106:108]))
    dwpc.append( float(line[112:114]))

    sknt.append( float(line[13:15]))
    if line[20:22] == '  ':
        gust.append( float(line[13:15]) )
    else:
        gust.append( float(line[20:22]))

    drct.append( float(line[16:19]) )
    alti.append( float(line[132:136]) / 100.0)

tmpc = temperature(np.array(tmpc), 'C')
dwpc = temperature(np.array(dwpc), 'C')
sknt = speed(np.array(sknt), 'KT')
gust = speed(np.array(gust), 'KT')

(fig, ax) = plt.subplots(3,1, sharex=True)

ax[0].plot(valid, tmpc.value("F"), color='r', label='Air')
ax[0].plot(valid, dwpc.value("F"), color='g', label='Dew Point')
ax[0].grid(True)
ax[0].legend(loc=2, ncol=2, fontsize=10)
ax[0].set_ylabel("Temperature $^\circ$F")
ax[0].set_title("22 July 2013 Knoxville AWOS Heat Burst\none minute interval data provided by Iowa DOT")

ax[1].plot(valid, sknt.value("MPH"), color='b', zorder=2, label='Speed')
ax[1].plot(valid, gust.value("MPH"), color='r', zorder=1, label='5s Gust')
ax1y2 = ax[1].twinx()
ax1y2.scatter(valid, drct)
ax1y2.set_xlim(0,361)
ax1y2.set_yticks([0,90,180,270,360])
ax1y2.set_yticklabels(('N', 'E', 'S', 'W', 'N'))
ax[1].legend(loc=(0.5, 1.0), ncol=2, fontsize=10)
ax[1].set_ylabel("Wind Speed [mph]")
ax1y2.set_ylabel("Wind Direction")
ax[1].grid(True)

ax[2].plot(valid, alti)
ax[2].set_xlim(valid[180], valid[270])
ax[2].grid(True)
ax[2].set_ylabel("Altimeter [inch]")
ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%I:%M', 
                                                     tz=pytz.timezone("America/Chicago")))
ax[2].set_xlabel("Evening of 22 July 2013 ")

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')