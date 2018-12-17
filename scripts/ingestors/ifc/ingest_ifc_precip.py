"""
  Process the IFC precip data!  Here's the file header
# file name: H99999999_I0007_G_15MAR2013_154000.out
# Rainrate map [mm/hr]
# number of columns: 1741
# number of rows: 1057
# grid: LATLON
# upper-left LATLONcorner(x,y): 6924 5409
# xllcorner [lon]: -97.154167
# yllcorner [lat]: 40.133331
# cellsize [dec deg]: 0.004167
# no data value: -99.0

http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/latest.dat
http://s-iihr57.iihr.uiowa.edu/feeds/IFC7ADV/H99999999_I0007_G_15MAR2013_154500.out
"""
from __future__ import print_function
import tempfile
import os
import datetime
import subprocess

import requests
import numpy as np
from PIL import Image
from PIL import PngImagePlugin
import pyiem.mrms as mrms
from pyiem.util import exponential_backoff

BASEURL = "http://rainproc.its.uiowa.edu/Products/IFC7ADV"


def get_file(now, routes):
    """ Download the file, save to /tmp and return fn """
    data = None
    for i in [7, 6, 5, 4]:
        if data is not None:
            break
        fn = now.strftime(("H99999999_I000" + repr(i) + "_G_%d%b%Y"
                           "_%H%M00")).upper()
        uri = "%s/%s.out" % (BASEURL, fn)
        req = exponential_backoff(requests.get, uri, timeout=5)
        if req is None:
            continue
        if req.status_code == 404:
            continue
        if req.status_code != 200:
            print(
                ("ingest_ifc_precip uri %s failed with status %s"
                 ) % (uri, req.status_code))
            continue
        data = req.content

    if data is None:
        # only generate an annoy-o-gram if we are in archive mode
        if routes == 'a':
            print("ingest_ifc_precip missing data for %s" % (now, ))
        return None
    tmpfn = tempfile.mktemp()
    fp = open(tmpfn, 'wb')
    fp.write(data)
    fp.close()
    return tmpfn


def to_raster(tmpfn, now):
    """ Convert the raw data into a RASTER Image
    5 inch rain per hour is ~ 125 mm/hr, so over 5min that is 10 mm
    Index 255 is missing
    0 is zero
    1 is 0.1 mm
    254 is 25.4 mm
    """
    data = np.loadtxt(tmpfn, skiprows=10)
    # mm/hr to mm/5min
    imgdata = (data * 10.0 / 12.0)
    imgdata = np.where(imgdata < 0, 255, imgdata)
    png = Image.fromarray(np.uint8(imgdata))
    png.putpalette(mrms.make_colorramp())
    meta = PngImagePlugin.PngInfo()
    meta.add_text('title', now.strftime("%Y%m%d%H%M"), 0)
    png.save('%s.png' % (tmpfn,), pnginfo=meta)
    del png
    # Make worldfile
    fp = open("%s.wld" % (tmpfn, ), 'w')
    fp.write("""0.004167
0.00
0.00
-0.004167
44.53785
-89.89942""")
    fp.close()


def ldm(tmpfn, now, routes):
    """ Send stuff to ldm """
    pq = "/home/ldm/bin/pqinsert"
    pqstr = ("%s -i -p 'plot %s %s gis/images/4326/ifc/p05m.wld "
             "GIS/ifc/p05m_%s.wld wld' %s.wld"
             "") % (pq, routes, now.strftime("%Y%m%d%H%M"),
                    now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = ("%s -i -p 'plot %s %s gis/images/4326/ifc/p05m.png "
             "GIS/ifc/p05m_%s.png png' %s.png"
             "") % (pq, routes, now.strftime("%Y%m%d%H%M"),
                    now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)


def cleanup(tmpfn):
    """Cleanup after ourselves"""
    os.remove(tmpfn)
    for suffix in ['png', 'wld']:
        os.remove("%s.%s" % (tmpfn, suffix))


def do_time(now, routes='ac'):
    """workflow"""
    tmpfn = get_file(now, routes)
    if tmpfn is None:
        return

    to_raster(tmpfn, now)

    ldm(tmpfn, now, routes)

    cleanup(tmpfn)


def main():
    """ main method """
    now = datetime.datetime.utcnow()
    now = now.replace(second=0, microsecond=0)
    # Round back to the nearest 5 minute, plus 10
    delta = now.minute % 5 + 15
    now = now - datetime.timedelta(minutes=delta)

    do_time(now)
    # Do we need to rerun a previous hour
    now = now - datetime.timedelta(minutes=60)
    fn = now.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/ifc/"
                       "p05m_%Y%m%d%H%M.png"))
    if not os.path.isfile(fn):
        do_time(now, routes='a')


if __name__ == '__main__':
    main()
