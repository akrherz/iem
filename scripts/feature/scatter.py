
import iemdb, math
import numpy
from matplotlib import pyplot as plt
ASOS = iemdb.connect("coop", bypass=True)
acursor = ASOS.cursor()



def wchtidx(tmpf, sped):
  if (sped < 3):
    return tmpf
  wci = math.pow(sped,0.16);

  return 35.74 + .6215 * tmpf - 35.75 * wci + \
     + .4275 * tmpf * wci

acursor.execute("""
SELECT day, high, snow
from alldata where stationid = 'ia0200' 
and year < 2011 ORDER by day ASC
""")
snow = []
highs = []
takenext = False
for row in acursor:
    if takenext:
        highs.append( float(row[1]) )
    if row[2] > 0:
        snow.append( float(row[2]) )
        takenext = True
    else:
        takenext = False

snow = numpy.array( snow )
highs = numpy.array( highs )

import numpy as np
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
axScatter.set_ylabel("Next Day High Temperature $^{\circ}\mathrm{F}$")
axScatter.set_xlabel("24 Hour Snowfall [in]")


xbins = np.arange(-0.5, 20, 1)
axHistx.hist(snow, bins=xbins)
#axHistx.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
axHistx.set_xlim( (-0.5, 20) )
axHistx.set_title("Ames Snowfall & Next Day High Temperature")
axHistx.grid(True)
axHistx.set_ylabel("Events")
#axHistx.set_yticks( numpy.arange(0,63*14,126))
#axHistx.set_yticklabels( numpy.arange(0,14,2) )


ybins = np.arange(-20,80, 5) 
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
