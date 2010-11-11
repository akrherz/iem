import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
ccursor2 = COOP.cursor()

ccursor.execute("""
SELECT year, max(high), sum(precip) from alldata where stationid = 'ia0200' GROUP by year
""")
doy = []
highs = []
rain = []
colors = []
for row in ccursor:

    ccursor2.execute("""SELECT extract(doy from day) from alldata 
    where stationid = 'ia0200' 
    and year = %s and high = %s""", (row[0], row[1]) )
    for row2 in ccursor2:
        doy.append( row2[0] )
        highs.append( row[1] )
        rain.append( row[2] )
        if row[2] > 32:
            colors.append('b')
        else:
            colors.append('r')
        if row[0] == 2010:
            print row, row2


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

doy = np.array( doy )
highs = np.array( highs )

nullfmt   = NullFormatter()         # no labels

# definitions for the axes
left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left+width+0.02

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]

# start with a rectangular Figure
fig = plt.figure(1, figsize=(8,8))


axScatter = plt.axes(rect_scatter)
axHistx = plt.axes(rect_histx)
axHisty = plt.axes(rect_histy)

# no labels
axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)

# the scatter plot:
axScatter.scatter(doy, highs, c=colors)

axScatter.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
axScatter.set_xticklabels( ("Jan","Feb","Mar","Apr","May 1","Jun 1","Jul 1","Aug 1","Sep 1","Oct 1","Nov","Dec") )

axScatter.set_xlim( (100, 300) )
axScatter.set_ylim( (85, 110) )
axScatter.grid(True)
axScatter.set_ylabel("Max Temperature $^{\circ}\mathrm{F}$")
axScatter.set_xlabel("Date of Max Temperature")
axScatter.scatter(195., 95., s=150, marker='+')

p1 = plt.Rectangle((0, 0), 1, 1, fc="r")
p2 = plt.Rectangle((0, 0), 1, 1, fc="b")
axScatter.legend((p1, p2), ('Below Avg Precip','Above Avg Precip'), loc=4, ncol=2)


xbins = np.arange(100., 300. + 0.5, 7)
axHistx.hist(doy, bins=xbins)
axHistx.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
axHistx.set_xlim( (100, 300) )
axHistx.set_title("Ames [1893-2010] Yearly Max Temperature")
axHistx.grid(True)

ybins = np.arange(85,110, 1) - 0.5
axHisty.hist(highs, bins=ybins, orientation='horizontal')
axHisty.grid(True)


axHisty.set_ylim( axScatter.get_ylim() )

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")