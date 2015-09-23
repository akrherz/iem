import datetime
import os
import urllib2
import pytz
import pygrib
from pyiem.plot import MapPlot
import numpy as np
from scipy.ndimage.filters import generic_filter

def dl(valid):
    ''' Get me files '''
    for hr in range(-15,0):
        ts = valid + datetime.timedelta(hours=hr)
        fn = ts.strftime("hrrr.ref.%Y%m%d%H00.grib2")
        if os.path.isfile(fn):
            continue
        uri = ts.strftime(("http://hrrr.agron.iastate.edu/data/"
                        +"hrrr_reflectivity/hrrr.ref.%Y%m%d%H00.grib2"))

        try:
            fp = open(fn, 'wb')
            fp.write( urllib2.urlopen(uri).read() )
            fp.close()
        except:
            print 'FAIL', uri
        
def compute(valid):
    ''' Get me files '''
    prob = None
    for hr in range(-15, 0):
        ts = valid + datetime.timedelta(hours=hr)
        fn = ts.strftime("/tmp/ncep_hrrr_%Y%m%d%H.grib2")
        print hr, fn
        if not os.path.isfile(fn):
            continue

        grbs = pygrib.open(fn)
        try:
            gs = grbs.select(level=1000,forecastTime=(-1 * hr * 60))
        except:
            print fn, 'ERROR'
            continue
        ref = gs[0]['values']
        #ref = generic_filter(gs[0]['values'], np.max, size=10)
        if prob is None:
            lats, lons = gs[0].latlons()
            prob = np.zeros( np.shape(ref) )
        
        prob = np.where(ref > 29, prob+1, prob)

    prob = np.ma.array(prob / 15. * 100.)
    prob.mask = np.ma.where(prob < 1, True, False)    
    
    m = MapPlot(sector='iowa',
                title='HRRR Composite Forecast 6 PM 22 Sep 2015 30+ dbZ Reflectivity',
                subtitle='frequency of previous 15 NCEP model runs all valid at %s' % (valid.astimezone(pytz.timezone("America/Chicago")).strftime("%-d %b %Y %I:%M %p %Z"),))

    m.pcolormesh(lons, lats, prob, np.arange(0,101,10), units='% of runs',
                     clip_on=False)
    m.map.drawcounties()
    m.postprocess(filename='test.png')
    m.close()
        
valid = datetime.datetime(2015,9,22,23)
valid = valid.replace(tzinfo=pytz.timezone("UTC"))

# dl(valid)

freq = compute(valid)
