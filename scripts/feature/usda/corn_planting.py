import numpy
import numpy.ma
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager
colors = ['red', 'black','green','teal','purple', 'blue']
fig, ax = plt.subplots(2,1)

progress = numpy.ma.zeros((2013-1979,52), 'f')
juliandate = numpy.ma.zeros((2013-1979,52), 'f')

lyear = 2013
x = []
y = []
ldiff = []
for line in open('crop_progress.csv').readlines()[1:]:
    tokens = line.split(",")
    ts = datetime.datetime.strptime(tokens[3], '%Y-%m-%d')
    if ts.year != lyear:
        if lyear in [1993,2013,2012, 2010,1984,1979,1991]:
            ax[0].plot( x, y, c=colors.pop(), 
                     label='%s' % (lyear,), lw=3, zorder=2)
        else:
            ax[0].plot( x, y, c='tan')
        lyear = ts.year
        y = numpy.array(y)
        diff = numpy.max( y[1:] - y[0:-1] )
        ldiff.append( diff )
        x = []
        y = []
    x.append( int(ts.strftime("%j")) )
    y.append( float(tokens[-1]) )
        
ax[0].plot( x, y, c='tan')
y = numpy.array(y)
diff = numpy.max( y[1:] - y[0:-1] )
ldiff.append( diff )
ldiff = numpy.array(ldiff)
prop = matplotlib.font_manager.FontProperties(size=12)


    
ax[0].legend(ncol=2, loc=4, prop=prop)
ax[0].set_xticks( (91,105,121,135,152,166, 182,213,244,274,305,335,365) )
ax[0].set_xticklabels( ('Apr 1','Apr 15', 'May 1', 'May 15', 'Jun 1', 'Jun 15', 'Jul 1','Aug','Sep','Oct','Nov','Dec') )
ax[0].set_xlim(90,170)
ax[0].grid(True)
ax[0].set_title("USDA Weekly Crop Progress Report (1979-2014)\nIowa Corn Planting Progress (6 years highlighted)")
ax[0].set_ylabel("Percent Planted [%]")

print len(ldiff)
ax[1].bar(numpy.arange(1979,2014)-0.4, ldiff[::-1])
ax[1].set_xlim(1978.5, 2013.5)
ax[1].set_ylabel("Max Weekly Change [%]")
ax[1].grid(True)

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')
