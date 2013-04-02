"""
 Generate a raster of 24hour precipitation totals from Q2

 run from RUN_10_AFTER.sh
 
 255 levels...  wanna do 0 to 20 inches
 
 0-1   -> 100 - 0.01 res
 1-5   -> 80 - 0.05 res
 5-20  -> 75 - 0.20 res
"""

import numpy
import mx.DateTime
import netCDF4
from PIL import Image
import os
import sys
import tempfile
import subprocess
import nmq
import json

def make_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/q2rad_hsr_nc/long_qpe/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )
    
def doit(gts, hr):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    szx = 7000
    szy = 3500
    west = -130.
    north = 55.
    sts = gts - mx.DateTime.RelativeDateTime(hours=hr)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': gts.strftime("%Y-%m-%dT%H:%M:%SZ") }
    # Create the image data
    imgdata = numpy.zeros( (szy, szx), 'u1')
    # Loop over tiles
    for tile in range(1,9):
        fp = make_fp(tile, gts)
        if not os.path.isfile(fp):
            #mesonet.bring_me_file( fp )
            print "q2_raster_%sh Missing Tile: %s Time: %s" % (hr, tile, gts)
            continue
        nc = netCDF4.Dataset( fp )
        # Our 24h rasters will support ~24 inch rainfalls
        hsr = nc.variables["rad_hsr_%sh" % (hr,)]
        val = hsr[:] / hsr.Scale # mm
        image = numpy.zeros( numpy.shape(val), 'i')
        """
         255 levels...  wanna do 0 to 20 inches
         index 255 is missing, index 0 is 0
         0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
         1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
         5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
        """
        image = numpy.where(val >= 500, 254, image)
        image = numpy.where(numpy.logical_and(val >= 125, val < 500), 180 + ((val - 125.) / 5.0), image)
        image = numpy.where(numpy.logical_and(val >= 25, val < 125), 100 + ((val - 25.) / 1.25), image)
        image = numpy.where(numpy.logical_and(val >= 0, val < 25), 0 + ((val - 0.) / 0.25), image)
        image = numpy.where( val < 0, 255, image)

        ysz, xsz = numpy.shape(val)
        x0 = (nmq.TILES[tile][0] - west) * 100.0
        y0 = (north - nmq.TILES[tile][1]) * 100.0
        #print tile, x0, xsz, y0, ysz, val[0,0]
        imgdata[y0:(y0+ysz-1),x0:(x0+xsz-1)] = image[:-1,:-1]
        nc.close()
    # Stress our color ramp
    #for i in range(256):
    #    imgdata[i*10:i*10+10,0:100] = i
    (tmpfp, tmpfn) = tempfile.mkstemp()
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( nmq.make_colorramp() )
    png.save('%s.png' % (tmpfn,))
    # Now we need to generate the world file
    nmq.write_worldfile('%s.wld' % (tmpfn,))
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
        gts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), 0)
    else:
        gts = mx.DateTime.gmtime() + mx.DateTime.RelativeDateTime(minute=0,second=0)
    for hr in [24,48,72]:
        doit( gts , hr)
        
    