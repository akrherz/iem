import pygrib
import os
import datetime
import numpy as np
from pyiem.plot import MapPlot
sts = datetime.datetime(2014, 11, 1, 0, 0)
ets = datetime.datetime(2014, 11, 22, 17, 0)
interval = datetime.timedelta(hours=1)


def do():
    now = sts
    while now < ets:
        fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2")
        if not os.path.isfile(fn):
            print fn
            now += interval
            continue
        grbs = pygrib.open(fn)
        try:
            gs = grbs.select(name='2 metre temperature')
        except:
            print fn
            now += interval
            continue

        g = gs[0]['values']
        if now == sts:
            lats,lons = gs[0].latlons()
            maxinterval = np.zeros(np.shape(g))
            current = np.zeros(np.shape(g))
        print np.max(g), np.min(g)
        current = np.where(g < 273, current + 1, 0)
        maxinterval = np.where(current > maxinterval, current, maxinterval)
        now += interval

    np.save('maxinterval.npy', np.array(maxinterval))
    np.save('lats.npy', lats)
    np.save('lons.npy', lons)

#do()
maxinterval = np.load('maxinterval.npy')
lats = np.load('lats.npy')
lons = np.load('lons.npy')

m = MapPlot(sector='conus', axisbg='#EEEEEE',
            title='1-22 November 2014 :: NCEP HRRR Maximum Period Below Freezing',
            subtitle='based on hourly HRRR 2 meter AGL Temperature Analysis, thru 22 Nov 12 PM CST')
m.pcolormesh(lons, lats, maxinterval, [1,3,6,12,24,48,72,5*24,7*24,
                                       9*24,11*24,13*24,15*24], units='time',
             clevlabels=['1h','3h','6h','12h','1d', '2',3,5,7,9,11,13,15])
m.postprocess(filename='test.png')
