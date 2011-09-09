import mx.DateTime
import urllib
import os

#http://torka.unl.edu/DroughtMonitor/Export/?mode=table&aoi=state&date=20000104
valid = []
d0 = []
d1 = []
d2 = []
d3 = []
d4 = []
sts = mx.DateTime.DateTime(2000,1,4)
ets = mx.DateTime.DateTime(2011,9,9)
interval = mx.DateTime.RelativeDateTime(days=7)
now = sts
while now < ets:
    """
    url = now.strftime("http://torka.unl.edu/DroughtMonitor/Export/?mode=table&aoi=state&date=%Y%m%d")
    cmd = "wget -q -O data/%s.dat '%s'" % (now.strftime("%Y%m%d"), url)
    os.system( cmd )
    now += interval
    """
    fp = "data/%s.dat" % (now.strftime("%Y%m%d"),)
    valid.append( float(now) )
    for line in open(fp):
        tokens = line.split(",")
        if tokens[1] == 'IA':
            d0.append( float(tokens[3]) )
            d1.append( float(tokens[4]) )
            d2.append( float(tokens[5]) )
            d3.append( float(tokens[6]) )
            d4.append( float(tokens[7]) )
            break
    now += interval

xticks = []
xticklabels = []
for yr in range(2000,2013):
    xticks.append( float(mx.DateTime.DateTime(yr,1,1)))
    xticklabels.append( yr )

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

fig = plt.figure()
ax= fig.add_subplot(111)

#ax.fill_between(valid, d0, 0, facecolor='#f6eb13', label='D0 Abnormal')
ax.bar(valid, d0, fc='#f6eb13', ec='#f6eb13', label='D0 Abnormal')
ax.bar(valid, d1, fc='#ffcc66', ec='#ffcc66', label='D1 Moderate')
ax.bar(valid, d2, fc='#ff9900', ec='#ff9900', label='D2 Severe')
ax.bar(valid, d3, fc='#ff3333', ec='#ff3333', label='D3 Extreme')
ax.bar(valid, d4, fc='#660000', ec='#660000', label='D4 Exceptional')
ax.set_xticks( xticks )
ax.set_xlim( min(xticks), max(valid))
ax.set_xticklabels( xticklabels)
ax.set_ylabel("Percentage of Iowa Area [%]")
ax.set_title("Areal coverage of Drought in Iowa\nfrom US Drought Monitor [1 Jan 2000 - 6 Sep 2011]")
ax.grid(True)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=5, prop=prop)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')