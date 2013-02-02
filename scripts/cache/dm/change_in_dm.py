import mx.DateTime
import urllib
import os
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

sts = mx.DateTime.DateTime(2000,1,4)
ets = mx.DateTime.DateTime(2012,11,8)
interval = mx.DateTime.RelativeDateTime(days=7)
now = sts
lastval = None
ld0 = None
ld1 = None
ld2 = None
ld3 = None
ld4 = None
while now < ets:
    fp = "data/%s.dat" % (now.strftime("%Y%m%d"),)
    for line in open(fp):
        tokens = line.split(",")
        if tokens[1] == 'IA':
            d0 = float(tokens[3]) 
            d1 = float(tokens[4]) 
            d2 = float(tokens[5]) 
            d3 = float(tokens[6])
            d4 = float(tokens[7]) 
            if lastval is None:
                ld0 = d0; ld1 = d1; ld2 = d2; ld3 = d3; ld4 = d4
            metric = (d0 - ld0) + 1. * (d1 - ld1) + 1. * (d2 - ld2) + 1. * (d3 - ld3) + 1. * (d4 - ld4)
            if lastval is None:
                lastval = metric
            lastval = metric
            print now, metric, tokens, ld0, ld1, ld2, ld3, ld4
            ld0 = d0; ld1 = d1; ld2 = d2; ld3 = d3; ld4 = d4
            if metric != 0:
                #ax.text(int(now.strftime("%j")), now.year, "%.1f" % (delta,))
                color = 'r'
                if metric < 0:
                    color = 'b'
                ax.arrow( int(now.strftime("%j")), now.year, 0.0, metric / 100.0, fc=color, ec=color,
head_width=5, head_length=0.1 )
            break
    now += interval

ax.set_ylim(2013,1999)
ax.set_ylabel("Year, thru 6 November 2012")
ax.set_title("2000-2012 US Drought Monitor Weekly Change for Iowa\narrow length represents change in intensity/coverage")
ax.set_xlim(0,366)
ax.set_xlabel("arrow length of 1 year is 1 effective category change over area of Iowa")
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.grid(True)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')
