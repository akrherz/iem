"""
 Generate a raster of data from raw Q2 netcdf files
 
 run from RUN_5MIN.sh

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
#import gdal

def make_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )

def doit(gts, varname, prefix):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    szx = 7000
    szy = 3500
    west = -130.
    north = 55.
    # Create the image data
    imgdata = numpy.zeros( (szy, szx), 'u1')
    if 'prefix' == 'r5m':
        sts = gts - mx.DateTime.RelativeDateTime(minutes=5)
    else:
        sts = gts - mx.DateTime.RelativeDateTime(minutes=60)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': gts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'product': prefix }
    # Loop over tiles
    for tile in range(1,9):
        fp = make_fp(tile, gts)
        if not os.path.isfile(fp):
            print "q2_raster Missing Tile: %s Time: %s" % (tile, gts)
            continue
        nc = netCDF4.Dataset( fp )
        hsr = nc.variables[varname]
        val = hsr[:] / hsr.Scale # convert to mm
        # Bump up by one, so that we can set missing to color index 0
        val += 1.0
        val = numpy.where(val < 1.0, 0., val)

        ysz, xsz = numpy.shape(val)
        x0 = (nmq.TILES[tile][0] - west) * 100.0
        y0 = (north - nmq.TILES[tile][1]) * 100.0
        #print tile, x0, xsz, y0, ysz, val[0,0], numpy.max( val )
        imgdata[y0:(y0+ysz-1),x0:(x0+xsz-1)] = val.astype('int')[:-1,:-1]
        nc.close()
    # Stress our color ramp
    #for i in range(256):
    #    imgdata[i*10:i*10+10,0:100] = i
    (tmpfp, tmpfn) = tempfile.mkstemp()
    
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( nmq.make_colorramp() )
    png.save('%s.png' % (tmpfn,))
    #test = gdal.Open('%s.png' % (tmpfn,), 0)
    #testd = test.ReadAsArray()
    #print testd[2632,3902], imgdata[2632,3902], numpy.max(testd), numpy.max(imgdata)
    # Now we need to generate the world file
    nmq.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/%s.png GIS/q2/%s_%s.wld wld' %s.wld" % (
                    gts.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/%s.png GIS/q2/%s_%s.png png' %s.png" % (
                    gts.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff -tr 1000.0 1000.0 %s.png %s.tif" % (tmpfn, tmpfn)
    subprocess.call(cmd, shell=True)
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/q2/%s.tif GIS/q2/%s_%s.tif tif' %s.tif" % (
                    gts.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    
    j = open("%s.json" % (tmpfn,), 'w')
    j.write( json.dumps(dict(meta=metadata)))
    j.close()
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/4326/q2/%s.json GIS/q2/%s_%s.json json' %s.json" % (
                    gts.strftime("%Y%m%d%H%M"),prefix, prefix, gts.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    for suffix in ['tif', 'json', 'png', 'wld']:
        os.unlink('%s.%s' % (tmpfn, suffix))

    os.close(tmpfp)
    os.unlink(tmpfn)

if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])), 
             "rad_hsr_1h", "n1p")
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])), 
             "preciprate_hsr", "r5m")
    else:
        gts = mx.DateTime.gmtime() - mx.DateTime.RelativeDateTime(minutes=10,second=0)
        offset = gts.minute % 5
        gts -= mx.DateTime.RelativeDateTime(minutes=offset)
        doit( gts, "rad_hsr_1h", "n1p")
        doit( gts, "preciprate_hsr", "r5m")
