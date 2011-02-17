
import iemdb, math
import numpy
from matplotlib import pyplot as plt
ASOS = iemdb.connect("asos", bypass=True)
acursor = ASOS.cursor()



def wchtidx(tmpf, sped):
  if (sped < 3):
    return tmpf
  wci = math.pow(sped,0.16);

  return 35.74 + .6215 * tmpf - 35.75 * wci + \
     + .4275 * tmpf * wci

#  min(case when extract(month from day) in (8,9) then low else 100 end), 
acursor.execute("""
    SELECT tmpf, sknt from alldata where station = 'DSM'
    and tmpf < 0 and sknt >= 3 and tmpf > -50 and sknt < 100""")
tmpf = []
wchill = []
for row in acursor:
  tmpf.append( float(row[0]) )
  wchill.append( wchtidx(row[0], row[1]) )


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

tmpf = np.array( tmpf )
wchill = np.array( wchill )

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
axScatter.scatter(tmpf, wchill, c='b', edgecolor='none',
                  s=50, alpha=0.05)

#axScatter.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
#axScatter.set_xticklabels( ("Jan","Feb","Mar","Apr","May 1","Jun 1","Jul 1","Aug 1","Sep 1","Oct 1","Nov","Dec") )

axScatter.set_xlim( (-30., 0.5) )
axScatter.set_ylim( (-50., 0.5) )
axScatter.grid(True)
axScatter.set_ylabel("Wind Chill $^{\circ}\mathrm{F}$")
axScatter.set_xlabel("Temperature $^{\circ}\mathrm{F}$ when wind > 2 knots")


xbins = np.arange(-30.5, 0. + 0.6, 1)
axHistx.hist(tmpf, bins=xbins)
#axHistx.set_xticks( (1,31,59,90,120,151,181,212,243,274,303,334) )
axHistx.set_xlim( (-30., 0.5) )
axHistx.set_title("Des Moines [1948-2010] Air Temperature & Wind Chill")
axHistx.grid(True)
axHistx.set_ylabel("Hours/Year")
axHistx.set_yticks( numpy.arange(0,63*14,126))
axHistx.set_yticklabels( numpy.arange(0,14,2) )


ybins = np.arange(-50.5,0.6, 1) 
axHisty.hist(wchill, bins=ybins, orientation='horizontal')
axHisty.grid(True)
axHisty.set_ylim( axScatter.get_ylim() )
axHisty.set_xlim(0,500)
axHisty.set_xticks( numpy.arange(0,63*8,63))
axHisty.set_xticklabels( numpy.arange(0,8) )
axHisty.set_xlabel("Hours/Year")

fig.savefig("110121.png", dpi=(40))
import iemplot
#iemplot.makefeature("test")
#plt.savefig("test.png")
