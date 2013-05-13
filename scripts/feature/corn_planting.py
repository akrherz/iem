import numpy
import numpy.ma
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
colors = ['red', 'black','green','teal','purple', 'yellow']
fig, ax = plt.subplots(1,1)

progress = numpy.ma.zeros((2013-1979,52), 'f')
juliandate = numpy.ma.zeros((2013-1979,52), 'f')

lyear = 2013
x = []
y = []
for line in open('crop_progress.csv').readlines()[1:]:
    tokens = line.split(",")
    ts = datetime.datetime.strptime(tokens[3], '%Y-%m-%d')
    if ts.year != lyear:
        if lyear in [1993,2013,2012, 2010,1984,1979,1991]:
            ax.plot( x, y, c=colors.pop(), 
                     label='%s' % (lyear,), lw=3)
        else:
            ax.plot( x, y, c='tan')
        lyear = ts.year
        x = []
        y = []
    x.append( int(ts.strftime("%j")) )
    y.append( float(tokens[-1]) )
        

prop = matplotlib.font_manager.FontProperties(size=12)


    
ax.legend(ncol=2, loc=4, prop=prop)
ax.set_xticks( (91,105,121,135,152,166, 182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Apr 1','Apr 15', 'May 1', 'May 15', 'Jun 1', 'Jun 15', 'Jul 1','Aug','Sep','Oct','Nov','Dec') )
ax.set_xlim(90,170)
ax.grid(True)
ax.set_title("USDA Weekly Crop Progress Report (1979-2012)\nIowa Corn Planting Progress (6 years highlighted)")
ax.set_ylabel("Percent Planted [%]")


fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')