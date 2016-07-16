"""
 Generate a composite of the MRMS XX Hour Precip total, easier than manually
 totalling it up myself.
"""
import datetime
import pytz
import numpy as np
import os
import tempfile
from PIL import Image
import subprocess
import json
import sys
import pyiem.mrms as mrms
import gzip
import pygrib

PQI = "/home/ldm/bin/pqinsert"


def do(now, hr):
    """ Generate for this timestep!
    255 levels...  wanna do 0 to 20 inches
     index 255 is missing, index 0 is 0
     0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
     1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
     5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
    """
    sts = now - datetime.timedelta(hours=hr)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'product': 'lcref',
                'units': 'mm'}
    gribfn = now.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/"
                           "RadarOnly_QPE_01H/"
                           "RadarOnly_QPE_01H_00.00_%Y%m%d-%H%M00.grib2.gz"))
    if not os.path.isfile(gribfn):
        print("mrms_raster_p1h.py MISSING %s" % (gribfn,))
        return
    fp = gzip.GzipFile(gribfn, 'rb')
    (_, tmpfn) = tempfile.mkstemp()
    tmpfp = open(tmpfn, 'wb')
    tmpfp.write(fp.read())
    tmpfp.close()
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)
    total = grb['values']

    # Off scale gets index 254
    imgdata = np.where(total >= 500, 254, 0)
    imgdata = np.where(np.logical_and(total >= 125, total < 500),
                       180 + ((total - 125.) / 5.0), imgdata)
    imgdata = np.where(np.logical_and(total >= 25, total < 125),
                       100 + ((total - 25.) / 1.25), imgdata)
    imgdata = np.where(np.logical_and(total >= 0, total < 25),
                       total / 0.25, imgdata)
    # -3 is no coverage -> 255
    # -1 is misisng, so zero
    # Index 255 is missing
    imgdata = np.where(total < 0, 0, imgdata)
    imgdata = np.where(total < -1, 255, imgdata)

    (tmpfp, tmpfn) = tempfile.mkstemp()
    # Create Image
    png = Image.fromarray(imgdata.astype('u1'))
    png.putpalette(mrms.make_colorramp())
    png.save('%s.png' % (tmpfn,))
    # os.system('xv %s.png' % (tmpfn,))
    mrms.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    prefix = 'p%sh' % (hr,)
    pqstr = ("%s -i -p 'plot ac %s gis/images/4326/mrms/%s.wld "
             "GIS/mrms/%s_%s.wld wld' %s.wld"
             ) % (PQI, now.strftime("%Y%m%d%H%M"), prefix, prefix,
                  now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = ("%s -p 'plot ac %s gis/images/4326/mrms/%s.png "
             "GIS/mrms/%s_%s.png png' %s.png"
             ) % (PQI, now.strftime("%Y%m%d%H%M"), prefix, prefix,
                  now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = ("gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
           "-tr 1000.0 1000.0 %s.png %s.tif"
           ) % (tmpfn, tmpfn)
    subprocess.call(cmd, shell=True)
    # Insert into LDM
    pqstr = ("%s -p 'plot c %s gis/images/900913/mrms/%s.tif "
             "GIS/mrms/%s_%s.tif tif' %s.tif"
             ) % (PQI, now.strftime("%Y%m%d%H%M"), prefix, prefix,
                  now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)

    j = open("%s.json" % (tmpfn,), 'w')
    j.write(json.dumps(dict(meta=metadata)))
    j.close()
    # Insert into LDM
    pqstr = ("%s -p 'plot c %s gis/images/4326/mrms/%s.json "
             "GIS/mrms/%s_%s.json json' %s.json"
             ) % (PQI, now.strftime("%Y%m%d%H%M"), prefix,
                  prefix, now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)
    for suffix in ['tif', 'json', 'png', 'wld']:
        os.unlink('%s.%s' % (tmpfn, suffix))

    os.close(tmpfp)
    os.unlink(tmpfn)


def main():
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
    if len(sys.argv) == 5:
        utcnow = datetime.datetime(int(sys.argv[1]),
                                   int(sys.argv[2]),
                                   int(sys.argv[3]),
                                   int(sys.argv[4]), 0).replace(
                                                tzinfo=pytz.timezone("UTC"))
        do(utcnow, 1)
    else:
        print 'Usage: python mrms_pXXh_comp.py YYYY MM DD HR'
        sys.exit(1)

if __name__ == '__main__':
    main()
