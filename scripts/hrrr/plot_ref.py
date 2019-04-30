"""
Generate an animated GIF of HRRR forecasted 1km reflectivity

Run from RUN_40AFTER.sh and for the previous hour's HRRR run
"""
from __future__ import print_function
import datetime
import subprocess
import sys
import os

import numpy as np
import pytz
import pygrib
from pyiem.plot import MapPlot
import pyiem.reference as ref
from pyiem.util import utc
HOURS = [
    36, 18, 18, 18, 18, 18,
    36, 18, 18, 18, 18, 18,
    36, 18, 18, 18, 18, 18,
    36, 18, 18, 18, 18, 18
]


def compute_bounds(lons, lats):
    """figure out a minimum box to extract data from, save CPU"""
    dist = ((lats - ref.MW_NORTH)**2 + (lons - ref.MW_WEST)**2)**0.5
    x2, y1 = np.unravel_index(dist.argmin(), dist.shape)
    dist = ((lats - ref.MW_SOUTH)**2 + (lons - ref.MW_EAST)**2)**0.5
    x1, y2 = np.unravel_index(dist.argmin(), dist.shape)
    return x1 - 100, x2 + 100, y1 - 100, y2 + 100


def run(valid, routes):
    ''' Generate the plot for the given UTC time '''
    fn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                         "hrrr.t%Hz.refd.grib2"))

    if not os.path.isfile(fn):
        print("hrrr/plot_ref missing %s" % (fn, ))
        return
    grbs = pygrib.open(fn)

    lats = None
    lons = None
    i = 0
    for minute in range(0, HOURS[valid.hour] * 60 + 1, 15):
        if minute > (18 * 60) and minute % 60 != 0:
            continue
        now = valid + datetime.timedelta(minutes=minute)
        now = now.astimezone(pytz.timezone("America/Chicago"))
        grbs.seek(0)
        try:
            gs = grbs.select(level=1000,
                             forecastTime=(minute
                                           if minute <= (18 * 60)
                                           else int(minute / 60)))
        except ValueError:
            continue
        if lats is None:
            lats, lons = gs[0].latlons()
            x1, x2, y1, y2 = compute_bounds(lons, lats)
            lats = lats[x1:x2, y1:y2]
            lons = lons[x1:x2, y1:y2]

        # HACK..............
        if len(gs) > 1 and minute > (18*60):
            reflect = gs[-1]['values'][x1:x2, y1:y2]
        else:
            reflect = gs[0]['values'][x1:x2, y1:y2]

        mp = MapPlot(sector='midwest', axisbg='tan',
                     title=('%s UTC NCEP HRRR 1 km AGL Reflectivity'
                            ) % (valid.strftime("%-d %b %Y %H"),),
                     subtitle=('valid: %s'
                               ) % (now.strftime("%-d %b %Y %I:%M %p %Z"),))

        mp.pcolormesh(lons, lats, reflect, np.arange(0, 75, 5), units='dBZ',
                      clip_on=False)
        pngfn = '/tmp/hrrr_ref_%s_%03i.png' % (valid.strftime("%Y%m%d%H"), i)
        mp.postprocess(filename=pngfn)
        mp.close()

        subprocess.call(("convert %s "
                         "%s.gif") % (pngfn, pngfn[:-4]), shell=True)

        i += 1

    # Generate anim GIF
    subprocess.call(("gifsicle --loopcount=0 --delay=50 "
                     "/tmp/hrrr_ref_%s_???.gif > /tmp/hrrr_ref_%s.gif"
                     ) % (valid.strftime("%Y%m%d%H"),
                          valid.strftime("%Y%m%d%H")),
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    pqstr = ("plot %s %s model/hrrr/hrrr_1km_ref.gif "
             "model/hrrr/hrrr_1km_ref_%02i.gif gif"
             ) % (routes, valid.strftime("%Y%m%d%H%M"), valid.hour)
    subprocess.call(("/home/ldm/bin/pqinsert -p '%s' /tmp/hrrr_ref_%s.gif"
                     ) % (pqstr, valid.strftime("%Y%m%d%H")),
                    shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    subprocess.call("rm -f /tmp/hrrr_ref_%s*" % (valid.strftime("%Y%m%d%H"), ),
                    shell=True)


def main(argv):
    """Go Main"""
    valid = utc(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]))
    now = utc()
    routes = 'a'
    if (now - valid) < datetime.timedelta(hours=2):
        routes = 'ac'

    # See if we already have output
    fn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/hrrr_1km_ref_%H.gif"
    )
    if not os.path.isfile(fn):
        run(valid, routes)


if __name__ == '__main__':
    # go go gadget
    main(sys.argv)
