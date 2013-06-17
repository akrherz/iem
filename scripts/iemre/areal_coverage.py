import netCDF4
from pyiem import iemre, plot
import numpy
import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sts = datetime.datetime(2013,4,1, 0)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2013,6,16, 0)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))


nc = netCDF4.Dataset('/mesonet/data/iemre/2013_mw_daily.nc')
lons = nc.variables['lon'][:]
lats = nc.variables['lat'][:]
precip = nc.variables['p01d']

nc2 = netCDF4.Dataset("/mesonet/data/iemre/state_weights.nc")
iowa = nc2.variables['IA'][:]
iowapts = numpy.sum(numpy.where(iowa > 0, 1, 0))
nc2.close()

days = []
coverage = []
now = sts
while now < ets:
    idx = iemre.daily_offset(now)
    pday = numpy.where(iowa > 0, precip[idx,:,:], -1)
    tots = numpy.sum(numpy.where(pday >= (0.05 * 25.4), 1, 0 ))
    days.append( now )
    coverage.append( tots / float(iowapts) * 100.0)
    
    now += datetime.timedelta(days=1)

days.append( now )
coverage.append( 0 )

days.append( now + datetime.timedelta(days=1))
coverage.append( 0 )

(fig, ax) = plt.subplots(1,1)

ax.bar(days, coverage, fc='b', ec='b')
ax.set_yticks([0,25,50,75,100])
ax.grid(True)
ax.set_title("2013 Daily Iowa Precipitation Coverage of 0.05+ inch")
ax.set_ylabel("Areal Coverage [%]")
ax.xaxis.set_major_locator(
                               mdates.DayLocator(interval=7)
                               )
ax.xaxis.set_major_formatter(mdates.DateFormatter('%-d\n%b'))
ax.set_xlim(min(days), max(days))

fig.savefig('test.svg')
import iemplot
iemplot.makefeature('test')