import netCDF4
import pygrib
from pyiem import iemre, plot
import numpy
import datetime
import pytz
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sts = datetime.datetime(2008,1,1, 0)
sts = sts.replace(tzinfo=pytz.timezone("UTC"))
ets = datetime.datetime(2013,1,1, 0)
ets = ets.replace(tzinfo=pytz.timezone("UTC"))


now = sts
counts = None
while now < ets:
    fn = "/mesonet/ARCHIVE/data/%s/stage4/ST4.%s.24h.grib" % (
      now.strftime("%Y/%m/%d"), now.strftime("%Y%m%d%H") )
    if not os.path.isfile(fn):
        now += datetime.timedelta(days=1)
        continue
    grb = pygrib.open(fn)
    g = grb.message(0)
    if counts is None:
        counts = numpy.zeros( numpy.shape(g['values']), 'f')
    if numpy.max(g['values']) > (4 * 25.4):
        print now
        counts += numpy.where(g['values'] > 4 * 25.4, 1, 0)
    now += datetime.timedelta(days=1)


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