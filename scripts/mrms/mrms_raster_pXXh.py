"""
 Generate a raster of 24hour precipitation totals from MRMS

 run from RUN_10_AFTER.sh
 
 255 levels...  wanna do 0 to 20 inches
 
 0-1   -> 100 - 0.01 res
 1-5   -> 80 - 0.05 res
 5-20  -> 75 - 0.20 res
"""

import numpy as np
import datetime
from PIL import Image
import os
import sys
import tempfile
import subprocess
import util
import json
import pygrib
import gzip

def doit(gts, hr):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    sts = gts - datetime.timedelta(hours=hr)
    times = [gts]
    if hr > 24:
        times.append(gts - datetime.timedelta(hours=24))
    if hr == 72:
        times.append( gts - datetime.timedelta(hours=48) )
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': gts.strftime("%Y-%m-%dT%H:%M:%SZ") }
    # Create the image data
    #imgdata = np.zeros( (szy, szx), 'u1')
    #timestep = np.zeros( (szy, szx), 'f')
    total = None
    for now in times:    
        gribfn = now.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/"
                +"RadarOnly_QPE_24H/"
                +"RadarOnly_QPE_24H_00.00_%Y%m%d-%H%M00.grib2.gz"))
        if not os.path.isfile(gribfn):
            print("mrms_raster_pXXh.py MISSING %s" % (gribfn,))
            return
        fp = gzip.GzipFile(gribfn, 'rb')
        (tmpfp, tmpfn) = tempfile.mkstemp()
        tmpfp = open(tmpfn, 'wb')
        tmpfp.write(fp.read())
        tmpfp.close()
        grbs = pygrib.open(tmpfn)
        grb = grbs[1]
        os.unlink(tmpfn)

        # careful here, how we deal with the two missing values!
        if total is None:
            total = grb['values']
        else:
            maxgrid = np.maximum(grb['values'], total)
            total = np.where(np.logical_and(grb['values'] >= 0,
                                           total >= 0),
                             grb['values'] + total, maxgrid)

    """
     255 levels...  wanna do 0 to 20 inches
     index 255 is missing, index 0 is 0
     0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
     1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
     5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
    """
    #total = np.flipud(total)
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
    imgdata = np.where( total < 0, 0, imgdata)
    imgdata = np.where( total < -1, 255, imgdata)
 
    (tmpfp, tmpfn) = tempfile.mkstemp()
    # Create Image
    png = Image.fromarray( imgdata.astype('u1') )
    png.putpalette( util.make_colorramp() )
    png.save('%s.png' % (tmpfn,))
    #os.system("xv %s.png" % (tmpfn,))
    # Now we need to generate the world file
    util.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/mrms/p%sh.wld GIS/mrms/p%sh_%s.wld wld' %s.wld" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/mrms/p%sh.png GIS/mrms/p%sh_%s.png png' %s.png" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff -tr 1000.0 1000.0 %s.png %s.tif" % (tmpfn, tmpfn)
    subprocess.call( cmd , shell=True)
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/mrms/p%sh.tif GIS/mrms/p%sh_%s.tif tif' %s.tif" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    
    j = open("%s.json" % (tmpfn,), 'w')
    j.write( json.dumps(dict(meta=metadata)))
    j.close()
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/4326/mrms/p%sh.json GIS/mrms/p%sh_%s.json json' %s.json" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    for suffix in ['tif', 'json', 'png', 'wld']:
        os.unlink('%s.%s' % (tmpfn, suffix))
    os.close(tmpfp)
    os.unlink(tmpfn)

if __name__ == "__main__":
    if len(sys.argv) == 5:
        gts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), 0)
    else:
        gts = datetime.datetime.utcnow()
        gts = gts.replace(minute=0,second=0,microsecond=0)
    for hr in [24,48,72]:
        doit( gts , hr)
