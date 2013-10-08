'''
Generate an animated GIF of HRRR forecasted 1km reflectivity

Run at ~ :15 after, from RUN_10_AFTER.sh

at 20:20 UTC, the 18z run is in.

'''

import pygrib
from pyiem.plot import MapPlot
import numpy as np
import datetime
import pytz
import subprocess
import os
import urllib2

def run( utc ):
    ''' Generate the plot for the given UTC time '''

    uri = utc.strftime(("http://hrrr.agron.iastate.edu/data/"
                        +"hrrr_reflectivity/hrrr.ref.%Y%m%d%H00.grib2"))

    fn = "/tmp/hrrr.ref.tmp.grib2"
    fp = open(fn, 'wb')
    fp.write( urllib2.urlopen(uri).read() )
    fp.close()

    grbs = pygrib.open(fn)

    subprocess.call("rm /tmp/hrrr_ref_???.gif", shell=True,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    lats = None
    lons = None
    i = 0
    for minute in range(0,901,15):
        now = utc + datetime.timedelta(minutes=minute)
        now = now.astimezone(pytz.timezone("America/Chicago"))
        grbs.seek(0)
        gs = grbs.select(level=1000,forecastTime=minute)
        if len(gs) == 0:
            continue
        g = gs[0]
        if lats is None:
            lats, lons = g.latlons()
        ref = g['values']

        m = MapPlot(sector='midwest',
                title='%s UTC HRRR 1 km AGL Reflectivity' % (
                                            utc.strftime("%-d %b %Y %H"),),
                subtitle='valid: %s' % (now.strftime("%-d %b %Y %I:%M %p %Z"),))

        m.pcolormesh(lons, lats, ref, np.arange(0,75,5), units='dBZ')
        m.postprocess(filename='/tmp/hrrr_ref_%03i.png' % (i,))
        m.close()
    
        subprocess.call(("convert /tmp/hrrr_ref_%03i.png "
                         +"/tmp/hrrr_ref_%03i.gif") % (i,i), shell=True)
    
        i += 1
    
    # Generate anim GIF
    subprocess.call(("gifsicle --loopcount=0 --delay=50 "
                         +"/tmp/hrrr_ref_???.gif > /tmp/hrrr_ref.gif"),
                shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    pqstr = ("plot ac %s model/hrrr/hrrr_1km_ref.gif "
             +"model/hrrr/hrrr_1km_ref_%02i.gif gif") % (
                            utc.strftime("%Y%m%d%H%M"), utc.hour)
    subprocess.call("/home/ldm/bin/pqinsert -p '%s' /tmp/hrrr_ref.gif" % (
                                                            pqstr,),
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    
    os.remove("/tmp/hrrr_ref.gif")
    os.remove("/tmp/hrrr.ref.tmp.grib2")


if __name__ == '__main__':
    ''' go go gadget '''
    utcnow = datetime.datetime.utcnow()
    utcnow = utcnow.replace(tzinfo=pytz.timezone("UTC"),minute=0,second=0,
                            microsecond=0)
    # Two hours ago
    utcnow = utcnow - datetime.timedelta(hours=2)
    run( utcnow )