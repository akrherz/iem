
import matplotlib.pyplot as plt
import numpy
import netCDF3

nc = netCDF3.Dataset('tmp.nc')
data = nc.variables['data'][:]


fig = plt.figure()
ax = fig.add_subplot(111)
d = numpy.arange(0,1440)
ax.plot(d, data[0], label='Jan', linewidth=3)
#ax.plot(d, data[1],'-.', label='Feb')
ax.plot(d, data[2], label='Mar', linewidth=3)
#ax.plot(d, data[3],label='Apr')
ax.plot(d, data[4],label='May', linewidth=3)
#ax.plot(d, data[5],label='Jun')
ax.plot(d, data[6],label='Jul', linewidth=3)
#ax.plot(d, data[7],label='Aug')
ax.plot(d, data[8],label='Sep', linewidth=3)
#ax.plot(d, data[9],label='Oct')
ax.plot(d, data[10],label='Nov', linewidth=3)
#ax.plot(d, data[11],label='Dec')

ax.set_xlim(-0.5,1439.5)
ax.set_xticks((0,4*60,8*60,12*60,16*60,20*60))
ax.set_xticklabels( ('Mid', '4 AM', '8 AM', 'Noon', '4 PM', '8 PM'))
ax.set_xlabel('All times CDT')
ax.set_ylabel('Temperature Departure $^{\circ}\mathrm{F}$')
ax.set_title('Des Moines Monthly Average Minute Temperature [2000-2010]')
ax.grid(True)
ax.legend(ncol=3,loc=4)
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')