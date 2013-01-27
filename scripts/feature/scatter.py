
import iemdb, math
import numpy
ASOS = iemdb.connect("coop", bypass=True)
acursor = ASOS.cursor()


acursor.execute("""
SELECT foo.day, foo.snow + foo3.s, foo2.high from
 (SELECT day, high, snow
 from alldata_ia where station = 'IA2203' 
 and snow >= 0.1) as foo,
 (SELECT day - '1 day'::interval as d, high, 
 case when snow > 0 then snow else 0 end as s
 from alldata_ia where station = 'IA2203') as foo3,
  (SELECT day + '1 day'::interval as d, high
 from alldata_ia where station = 'IA2203' and (snow is null or snow = 0)) as foo2
 WHERE foo3.d = foo2.d and foo2.d = foo.day ORDER
 by foo.day ASC
""")
snow = []
highs = []
takenext = False
for row in acursor:
    highs.append( row[2] )
    snow.append( row[1] )
    print row

snow = numpy.array( snow )
highs = numpy.array( highs )

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter


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
axScatter.scatter(snow, highs, c='b', edgecolor='none',
                  s=50, alpha=0.1)
axScatter.plot([0,20],[32,32], c='r')

#axScatter.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
#axScatter.set_xticklabels( ("Jan","Feb","Mar","Apr","May 1","Jun 1","Jul 1","Aug 1","Sep 1","Oct 1","Nov","Dec") )

axScatter.set_xlim( (-0.5, 20) )
axScatter.set_ylim( (-20., 80) )
axScatter.grid(True)
axScatter.set_ylabel("Previous Day High Temperature $^{\circ}\mathrm{F}$")
axScatter.set_xlabel("48 Hour Snowfall [in]")


xbins = numpy.arange(-0.5, 20, 1)
axHistx.hist(snow, bins=xbins)
#axHistx.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
axHistx.set_xlim( (-0.5, 20) )
axHistx.set_title("Des Moines 48 HR Snowfall & Previous Day High Temperature")
axHistx.grid(True)
axHistx.set_ylabel("Events")
#axHistx.set_yticks( numpy.arange(0,63*14,126))
#axHistx.set_yticklabels( numpy.arange(0,14,2) )


ybins = numpy.arange(-20,80, 5) 
axHisty.hist(highs, bins=ybins, orientation='horizontal')
axHisty.grid(True)
axHisty.set_ylim( axScatter.get_ylim() )
axHisty.set_xlim(0,400)
axHisty.set_xticks( numpy.arange(0,400,100))
#axHisty.set_xticklabels( numpy.arange(0,8) )
axHisty.set_xlabel("Events")

fig.savefig("test.ps")
import iemplot
iemplot.makefeature("test")
#plt.savefig("test.png")
