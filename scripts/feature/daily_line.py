import matplotlib.pyplot as plt
import numpy
import netCDF3

nc = netCDF3.Dataset('tmp2.nc')
data = nc.variables['data'][:]

highs = numpy.zeros((365,), 'f')
lows = numpy.zeros((365,), 'f')

for i in range(365):
    mn = numpy.min(data[i,240:720])
    mx = numpy.max(data[i,720:1440])
    print numpy.average( numpy.where(data[i,:]==mn) )
    highs[i] = numpy.average( numpy.where(data[i,720:1440]==mx) ) + 720
    lows[i] = numpy.average( numpy.where(data[i,240:720]==mn) ) + 240


fig = plt.figure()
ax = fig.add_subplot(111)
d = numpy.arange(0,365)

ax.scatter(d, highs, color='r',  label='High')
ax.scatter(d, lows, color='b', label='Low')

ax.set_ylim(-0.5,1439.5)
ax.set_yticks((0,4*60,8*60,12*60,16*60,20*60))
ax.set_yticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_ylabel('All times CDT')
#ax.set_ylabel('Temperature Departure $^{\circ}\mathrm{F}$')
ax.set_title('Des Moines Time of Day when High/Low are set [2000-2010]')

ax.set_xlim(0,366)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )

ax.grid(True)
ax.legend(ncol=3,loc=4)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')