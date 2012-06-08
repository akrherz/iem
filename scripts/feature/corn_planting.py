import numpy
import numpy.ma
import mx.DateTime.ISO

progress = numpy.ma.zeros((2013-1979,52), 'f')
juliandate = numpy.ma.zeros((2013-1979,52), 'f')
largest = numpy.zeros((2013-1979))

for line in open('crop_progress.csv').readlines()[1:]:
    tokens = line.split(",")
    year = int(tokens[0])
    week = int(tokens[2][7:9])
    p = tokens[4]
    if p != '" "':
        val = int(tokens[4])
        progress[year-1979,week-1] = val
        ts = mx.DateTime.ISO.WeekTime(year,week) + mx.DateTime.RelativeDateTime(days=6)
        juliandate[year-1979,week-1] = int(ts.strftime("%j"))
        diff = val - progress[year-1979,week-1-1]
        if diff > largest[year-1979]:
            largest[year-1979] = diff
        
progress.mask = numpy.where(progress == 0, True, False)

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
prop = matplotlib.font_manager.FontProperties(size=12)

colors = ['red', 'black','green','teal','purple', 'yellow']
fig, ax = plt.subplots(2,1)

for yr in range(1979,2013):
    if yr in [1993,2012,2010,1984,1979,1991]:
        ax[0].plot( juliandate[yr-1979,:], progress[yr-1979,:], c=colors.pop(), 
                 label='%s' % (yr,), lw=3)
    else:
        ax[0].plot( juliandate[yr-1979,:], progress[yr-1979,:], c='tan')
    
ax[0].legend(ncol=2, loc=4, prop=prop)
ax[0].set_xticks( (91,105,121,135,152,166, 182,213,244,274,305,335,365) )
ax[0].set_xticklabels( ('Apr 1','Apr 15', 'May 1', 'May 15', 'Jun 1', 'Jun 15', 'Jul 1','Aug','Sep','Oct','Nov','Dec') )
ax[0].set_xlim(90,170)
ax[0].grid(True)
ax[0].set_title("USDA Weekly Crop Progress Report (1979-2012)\nIowa Corn Planting Progress (6 years highlighted)")
ax[0].set_ylabel("Percent Planted [%]")


ax[1].bar( numpy.arange(1979,2013)-0.4, largest)
ax[1].set_ylabel("Largest Weekly Change [%]")
ax[1].set_xlim(1978.5,2012.5)
ax[1].grid(True)

fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')