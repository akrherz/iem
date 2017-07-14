"""Convert HRRR Grib Reflectivity to RASTERS matching IEM N0Q

Won't be archiving these ATTM, for "realtime"
  data/gis/images/4326/hrrr/refd_fMMMM.png  where MMMM is 4 char minutes



"""
from __future__ import print_function
import sys
import os
import datetime
import tempfile
import subprocess
import json

import numpy as np
import pygrib
import pytz
from PIL import Image

PALETTE = Image.open(open("/home/ldm/data/gis/images/4326/USCOMP/n0q_0.png")
                     ).getpalette()


def do_grb(grib, valid):
    """Process this grib object"""
    fxminutes = grib.forecastTime
    fxvalid = valid + datetime.timedelta(minutes=fxminutes)
    gribtemp = tempfile.NamedTemporaryFile(suffix=".grib2", delete=False)
    newgribtemp = tempfile.NamedTemporaryFile(suffix=".grib2")
    pngtemp = tempfile.NamedTemporaryFile(suffix='.png')
    gribtemp.write(grib.tostring())
    gribtemp.close()
    # Regrid this to match N0Q
    cmd = ("wgrib2 %s -set_grib_type same -new_grid_winds earth "
           "-new_grid latlon -126:3050:0.02 23.01:1340:0.02 %s"
           ) % (gribtemp.name, newgribtemp.name)
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
    # Rasterize
    grbs = pygrib.open(newgribtemp.name)
    g1 = grbs[1]
    refd = np.flipud(g1.values)
    # anything -10 or lower is zero
    refd = np.where(refd < -9, -99, refd)
    # rasterize from index 1 as -32 by 0.5
    raster = ((refd + 32.0) * 2. + 1)
    raster = np.where(np.logical_or(raster < 1, raster > 255), 0,
                      raster).astype(np.uint8)
    png = Image.fromarray(raster)
    png.putpalette(PALETTE)
    png.save(pngtemp)
    cmd = ("/home/ldm/bin/pqinsert -i -p 'plot c %s gis/images/4326/hrrr/"
           "refd_%04i.png bogus png' %s"
           ) % (valid.strftime("%Y%m%d%H%M"), fxminutes, pngtemp.name)
    subprocess.call(cmd, shell=True)
    # Do world file variant
    wldtmp = tempfile.NamedTemporaryFile(delete=False)
    wldtmp.write("""0.02
0.0
0.0
-0.02
-126.0
50.0""")
    wldtmp.close()
    cmd = ("/home/ldm/bin/pqinsert -i -p 'plot c %s gis/images/4326/hrrr/"
           "refd_%04i.wld bogus wld' %s"
           ) % (valid.strftime("%Y%m%d%H%M"), fxminutes, wldtmp.name)
    subprocess.call(cmd, shell=True)
    # Do json metadata
    jsontmp = tempfile.NamedTemporaryFile(delete=False)
    jdict = {'model_init_utc': valid.strftime("%Y-%m-%dT%H:%M:%SZ"),
             'forecast_minute': fxminutes,
             'model_forecast_utc': fxvalid.strftime("%Y-%m-%dT%H:%M:%SZ")}
    json.dump(jdict, jsontmp)
    jsontmp.close()
    cmd = ("/home/ldm/bin/pqinsert -i -p 'plot c %s gis/images/4326/hrrr/"
           "refd_%04i.json bogus json' %s"
           ) % (valid.strftime("%Y%m%d%H%M"), fxminutes, jsontmp.name)
    subprocess.call(cmd, shell=True)
    os.unlink(gribtemp.name)
    os.unlink(wldtmp.name)
    os.unlink(jsontmp.name)


def workflow(valid):
    """Process this time's data"""
    gribfn = valid.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
                             "hrrr.t%Hz.refd.grib2"))
    if not os.path.isfile(gribfn):
        print("hrrr_ref2raster.py missing %s" % (gribfn, ))
        return
    grbs = pygrib.open(gribfn)
    for i in range(grbs.messages):
        do_grb(grbs[i + 1], valid)


def main(argv):
    """So Something great"""
    valid = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]),
                              int(argv[4])).replace(tzinfo=pytz.utc)
    workflow(valid)


if __name__ == '__main__':
    main(sys.argv)
