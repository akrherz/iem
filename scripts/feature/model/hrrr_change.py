import pygrib
import os
import datetime
import numpy as np
from pyiem.plot import MapPlot
from pyiem.datatypes import temperature
sts = datetime.datetime(2015, 3, 16, 12, 0)
ets = datetime.datetime(2015, 3, 18, 11, 0)
interval = datetime.timedelta(hours=1)


def do():
    now = sts
    while now < ets:
        fn = now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2")
        fn2 = (now - datetime.timedelta(hours=24)).strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2")
        if not os.path.isfile(fn) or not os.path.isfile(fn2):
            print fn, fn2
            now += interval
            continue
        grbs = pygrib.open(fn)
        try:
            gs = grbs.select(name='2 metre temperature')
        except:            
            print fn
            now += interval
            continue

        grbs2 = pygrib.open(fn2)
        try:
            gs2 = grbs2.select(name='2 metre temperature')
        except:            
            print fn2
            now += interval
            continue
        
        g = temperature(gs[0]['values'], 'K')
        g2 = temperature(gs2[0]['values'], 'K')
        if now == sts:
            lats,lons = gs[0].latlons()
            largest = np.zeros(np.shape(g))
        delta = g.value('F') - g2.value('F')
        largest = np.minimum(delta, largest)
        now += interval
    
    np.save('maxinterval.npy', np.array(largest))
    np.save('lats.npy', lats)
    np.save('lons.npy', lons)
        
#do()
#sys.exit()
maxinterval = np.load('maxinterval.npy')
print np.max(maxinterval), np.min(maxinterval)
lats = np.load('lats.npy')
lons = np.load('lons.npy')

m = MapPlot(sector='conus', axisbg='#EEEEEE',
            title='16 - 18 March 2015 :: Coldest 24 Hour Temperature Change',
            subtitle='based on hourly HRRR Analyses 7 AM 16 Mar thru 5 AM 18 Mar')
m.pcolormesh(lons, lats, maxinterval, range(-50,1,5), units='F')
m.postprocess(filename='test.png')
