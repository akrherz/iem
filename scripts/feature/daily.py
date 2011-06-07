import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

acursor.execute("""
select doy, count(*), sum(case when t >=80 then 1 else 0 end), sum(case when t >= 80 and d < 60 then 1 else 0 end) from (select extract(year from valid) as year, extract(doy from valid) as doy, max(tmpf) as t, max(dwpf) as d from alldata where station = 'DSM' and extract(hour from valid) between 11 and 19 GROUP by year, doy) as foo GROUP by doy ORDER by doy
""")

import datetime
data = [0]* 366
for row in acursor:
    if row[2] > 0:
        data[int(row[0])-1] = float(row[3]) / float(row[2]) * 100.0



import mx.DateTime
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure()
ax = fig.add_subplot(111)

xticks = []
xticklabels = []
sts = mx.DateTime.DateTime(2000,4,1)
ets = mx.DateTime.DateTime(2000,12,1)
interval = mx.DateTime.RelativeDateTime(months=1)
now = sts
while now < ets:
  xticks.append( (now - mx.DateTime.DateTime(2000,1,1)).days )
  xticklabels.append( now.strftime("%-d %b") )
  now += interval

bars = ax.bar( np.arange(1,len(data)+1) - 0.3, data, facecolor='r', edgecolor='r')
for bar in bars:
    if bar.get_height() > 100:
        bar.set_facecolor('blue')
        bar.set_edgecolor('blue')
ax.set_xlim(0.5, len(data)+1)
ax.set_xticks(xticks)
ax.set_xlim(min(xticks)-1, max(xticks)+1)
ax.set_xticklabels(xticklabels)
ax.set_ylabel("Frequency [%]")
#ax.set_xlabel("1 Jan - 26 May 2011")
ax.set_title("Des Moines Days when Afternoon High over 80 $^{\circ}\mathrm{F}$\nFrequency of Maximum Dew Point under 60 $^{\circ}\mathrm{F}$ [1949-2011]")
ax.grid(True)

"""
sts = mx.DateTime.DateTime(2011,1,1)
j = 0
ax.text(10,175, 'Days over 100', size=16)
for i in range(len(data)):
    if data[i] >= 100:
        ets = sts + mx.DateTime.RelativeDateTime(days=i)
        txt = "%s. %s - %s" % (j+1, ets.strftime("%b %d"), data[i])
        ax.text(10, 150-(j*24), txt, size=16)
        j += 1
"""
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
