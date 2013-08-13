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
import gzip
from PIL import Image
import os
import sys
import tempfile
import subprocess
import util
import json

def doit(gts, hr):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    szx = 7000
    szy = 3500

    sts = gts - datetime.timedelta(hours=hr)
    times = [gts]
    if hr > 24:
        times.append(gts - datetime.timedelta(hours=24))
    if hr == 72:
        times.append( gts - datetime.timedelta(hours=48) )
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': gts.strftime("%Y-%m-%dT%H:%M:%SZ") }
    # Create the image data
    imgdata = np.zeros( (szy, szx), 'u1')
    timestep = np.zeros( (szy, szx), 'f')
    for now in times:    
        for tile in range(1,5):
            fn = util.get_fn('24hrad', now, tile)
            if not os.path.isfile(fn):
                print 'MRMS 24h RASTER missing %s' % (fn,)
                continue
        
            tilemeta, val = util.reader(fn)
            ysz, xsz = np.shape(val)
            val = np.flipud(val)
            x0 = (tilemeta['ul_lon'] - util.WEST) * 100.0
            y0 = (util.NORTH - tilemeta['ul_lat']) * 100.0
            timestep[y0:(y0+ysz),x0:(x0+xsz)] += val
            """
             255 levels...  wanna do 0 to 20 inches
             index 255 is missing, index 0 is 0
             0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
             1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
             5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
            """
            
    imgdata = np.where(timestep >= 500, 254, imgdata)
    imgdata = np.where(np.logical_and(timestep >= 125, timestep < 500), 
                       180 + ((timestep - 125.) / 5.0), imgdata)
    imgdata = np.where(np.logical_and(timestep >= 25, timestep < 125), 
                       100 + ((timestep - 25.) / 1.25), imgdata)
    imgdata = np.where(np.logical_and(timestep >= 0, timestep < 25), 
                       0 + ((timestep - 0.) / 0.25), imgdata)
    imgdata = np.where( timestep < 0, 255, imgdata)

    # Stress our color ramp
    #for i in range(256):
    #    imgdata[i*10:i*10+10,0:100] = i
    (tmpfp, tmpfn) = tempfile.mkstemp()
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( util.make_colorramp() )
    png.save('%s.png' % (tmpfn,))
    # Now we need to generate the world file
    util.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/p%sh.wld GIS/q2/p%sh_%s.wld wld' %s.wld" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/p%sh.png GIS/q2/p%sh_%s.png png' %s.png" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff -tr 1000.0 1000.0 %s.png %s.tif" % (tmpfn, tmpfn)
    subprocess.call( cmd , shell=True)
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/q2/p%sh.tif GIS/q2/p%sh_%s.tif tif' %s.tif" % (
                    gts.strftime("%Y%m%d%H%M"),hr, hr, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    
    j = open("%s.json" % (tmpfn,), 'w')
    j.write( json.dumps(dict(meta=metadata)))
    j.close()
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/4326/q2/p%sh.json GIS/q2/p%sh_%s.json json' %s.json" % (
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
        
    