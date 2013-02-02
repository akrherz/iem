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
sts = mx.DateTime.DateTime(2012,1,3)
ets = mx.DateTime.DateTime(2012,11,8)
interval = mx.DateTime.RelativeDateTime(days=7)
now = sts
while now < ets:
    #"""
    url = now.strftime("http://torka.unl.edu/DroughtMonitor/Export/?mode=table&aoi=state&date=%Y%m%d")
    cmd = "wget -q -O data/%s.dat '%s'" % (now.strftime("%Y%m%d"), url)
    os.system( cmd )
    now += interval
    """
    fp = "/mesonet/data/dm/text/%s.dat" % (now.strftime("%Y%m%d"),)
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
    """
xticks = []
xticklabels = []
for yr in range(1,13):
    xticks.append( float(mx.DateTime.DateTime(2012,yr,1)))
    fmt = "%b"
    if yr == 1:
        fmt = "%b\n%Y"
    xticklabels.append( mx.DateTime.DateTime(2012,yr,1).strftime(fmt) )
#for yr in range(2000,2013,2):
#    xticks.append( float(mx.DateTime.DateTime(yr,1,1)))
#    fmt = "%Y"
#    if 1 == 2:
#        fmt = "%b\n%Y"
#    xticklabels.append( mx.DateTime.DateTime(yr,1,1).strftime(fmt) )
import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

fig = plt.figure()
ax= fig.add_subplot(111)

#ax.fill_between(valid, d0, 0, facecolor='#f6eb13', label='D0 Abnormal')
ax.bar(valid, d0, width=7*86400, fc='#f6eb13', ec='#f6eb13', label='D0 Abnormal')
ax.bar(valid, d1, width=7*86400, fc='#ffcc66', ec='#ffcc66', label='D1 Moderate')
ax.bar(valid, d2, width=7*86400, fc='#ff9900', ec='#ff9900', label='D2 Severe')
ax.bar(valid, d3, width=7*86400, fc='#ff3333', ec='#ff3333', label='D3 Extreme')
ax.bar(valid, d4, width=7*86400, fc='#FF00FF', ec='#FF00FF', label='D4 Exceptional')

print d4

#ax.annotate("",
#       xytext=(float(mx.DateTime.DateTime(2011,9,1)), 10), xycoords='data',
#       xy=(float(mx.DateTime.DateTime(2011,12,1)), 25), textcoords='data',
#       arrowprops=dict(arrowstyle="->",
#                            connectionstyle="arc3"),
#       )
#ax.annotate("",
#       xy=(float(mx.DateTime.DateTime(2011,12,8)), 65), xycoords='data',
#       xytext=(float(mx.DateTime.DateTime(2011,11,1)), 85), textcoords='data',
#       arrowprops=dict(arrowstyle="->",
#                            connectionstyle="arc3"),
#       )


ax.set_xticks( xticks )
ax.set_ylim(0,100)
#ax.set_xlabel("D4 Only on 4 Sep 2012 at 2.4%")
ax.set_xlim( min(xticks), max(valid)+14*86400+100)
ax.set_xticklabels( xticklabels)
ax.set_ylabel("Percentage of Iowa Area [%]")
ax.set_title("2012 Areal coverage of Drought in Iowa\nfrom US Drought Monitor")
ax.grid(True)
#ax.legend(loc='upper center', bbox_to_anchor=(0.7, 1),
#          fancybox=True, shadow=True, ncol=1, prop=prop)
ax.legend(loc='best', ncol=1)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
