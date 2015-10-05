import matplotlib.pyplot as plt
import os
import mx.DateTime
import re
import numpy 

sts = mx.DateTime.DateTime(2012,1,1,12)
ets = mx.DateTime.DateTime(2012,5,11,12)
interval = mx.DateTime.RelativeDateTime(hours=24)
now = sts
vals = []
valid = []
xticks = []
xticklabels = []
while now < ets:
    fp = now.strftime("/mnt/a4/data/%Y/%m/%d/bufkit/%H/nam/nam_kdsm.buf")
    if not os.path.isfile(fp):
      vals.append( vals[-1] )
      valid.append( now.ticks() )
      now += interval
      continue
    data = open(fp,'r').read().replace("\n","")
    tokens = re.findall("PWAT = (\d+\.\d+)", data)
    vals.append( float(tokens[0]) / 25.4)
    valid.append( now.ticks() )
    if now.day == 1 or now.day % 7 == 0:
        fmt = '%-d'
        if now.day == 1:
            fmt = '%-d\n%b'
        xticks.append( now.ticks() )
        xticklabels.append( now.strftime(fmt) )
    now += interval


fig, ax = plt.subplots(1,1)

ax.bar(valid, vals, edgecolor='b', facecolor='b',width=86400)
ax.set_xticks(xticks)
ax.set_xticklabels( xticklabels )
ax.set_title("NAM Precipitable Water Analysis for Des Moines")
ax.set_ylabel("Precipitable Water [inch]")
ax.set_xlabel("2012")
ax.set_xlim(min(xticks), max(xticks)+192000)
ax.grid(True)
fig.savefig('test.png')
