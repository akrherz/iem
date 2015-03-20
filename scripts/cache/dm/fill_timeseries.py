import os
import datetime

valid = []
xd0 = []
xd1 = []
xd2 = []
xd3 = []
xd4 = []
for line in open('iowa.txt').read().split("\n")[::-1]:
    if line.strip() == '':
        continue
    (tstamp, noval, d0, d1, d2, d3, d4) = line.split("\t")
    valid.append((datetime.datetime.strptime(tstamp, '%Y-%m-%d')).date())
    xd0.append(float(d0))
    xd1.append(float(d1))
    xd2.append(float(d2))
    xd3.append(float(d3))
    xd4.append(float(d4))

print valid

import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=10)

fig = plt.figure()
ax= fig.add_subplot(111)

#ax.fill_between(valid, d0, 0, facecolor='#f6eb13', label='D0 Abnormal')
ax.bar(valid, xd0, width=7, fc='#f6eb13', ec='#f6eb13', label='D0 Abnormal')
ax.bar(valid, xd1, width=7, fc='#ffcc66', ec='#ffcc66', label='D1 Moderate')
ax.bar(valid, xd2, width=7, fc='#ff9900', ec='#ff9900', label='D2 Severe')
ax.bar(valid, xd3, width=7, fc='#ff3333', ec='#ff3333', label='D3 Extreme')
ax.bar(valid, xd4, width=7, fc='#FF00FF', ec='#FF00FF', label='D4 Exceptional')


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


#ax.set_xticks( xticks )
ax.set_ylim(0,100)
ax.set_yticks([0,10,30,50,70,90,100])
#ax.set_xlabel("D4 Only on 4 Sep 2012 at 2.4%")
#ax.set_xlim( min(xticks), max(valid)+7*86400+100)
#ax.set_xticklabels( xticklabels)
ax.set_ylabel("Percentage of Iowa Area [%]")
ax.set_title("2000-2015 Areal coverage of Drought in Iowa\nfrom US Drought Monitor")
ax.grid(True)
#ax.legend(loc='upper center', bbox_to_anchor=(0.7, 1),
#          fancybox=True, shadow=True, ncol=1, prop=prop)
ax.legend(loc=(-0.1, -0.1), ncol=5, prop=prop)
fig.savefig('test.png')
