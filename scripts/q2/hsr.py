# Generate a GIS raster from the 8 NMQ data tiles! :)

import numpy
import mx.DateTime
try:
    import netCDF3
except:
    import netCDF4 as netCDF3
from PIL import Image
import os
import sys

# NW Corner of tiles
tiles = {
         1: [-130., 55.],
         2: [-110., 55.],
         3: [-90., 55.],
         4: [-80., 55.],
         5: [-130., 40.],
         6: [-110., 40.],
         7: [-90., 40.],
         8: [-80., 40.]
         }

def make_colorramp():
    """
    Make me a crude color ramp
    """
    c = numpy.zeros((256,3), numpy.int)
    
    # Gray for missing
    c[0,:] = [144,144,144]
    # Black to remove, eventually
    c[1,:] = [0,0,0]
    i = 2 
    for line in open('gr2ae.txt'):
      c[i,:] = map(int, line.split()[-3:])
      i+=1
    return tuple( c.ravel() )

def make_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/mosaic2d_nc/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )
    
def doit(gts):
    """
    Actually generate a PNG file from the 8 NMQ tiles
    """
    szx = 7000
    szy = 3500
    west = -130.
    north = 55.
    # Create the image data
    imgdata = numpy.zeros( (szy, szx), 'u1')
    # Loop over tiles
    for tile in range(1,9):
        fp = make_fp(tile, gts)
        if not os.path.isfile(fp):
            print "Missing", fp
            continue
        nc = netCDF3.Dataset( fp )
        val = nc.variables["hsr"][:,:] / 10.0 # convert to dBZ
        # -99 is no return
        # -999 is missing
        #print "1. Min: %.2f  Avg: %.2f Max: %.2f" % (numpy.min(val), numpy.average(val),
        #                                             numpy.max(val))
        # Move the good data
        val = numpy.where( val > -33., (val +32.) * 2.0, val)
        #print "2. Min: %.2f  Avg: %.2f Max: %.2f" % (numpy.min(val), numpy.average(val),
        #                                             numpy.max(val))
        val = numpy.where( val < -990., 0., val)
        #print "3. Min: %.2f  Avg: %.2f Max: %.2f" % (numpy.min(val), numpy.average(val),
        #                                             numpy.max(val))
        val = numpy.where( val < 0., 1., val)
        #print "4. Min: %.2f  Avg: %.2f Max: %.2f" % (numpy.min(val), numpy.average(val),
        #                                             numpy.max(val))
        ysz, xsz = numpy.shape(val)
        x0 = (tiles[tile][0] - west) * 100.0
        y0 = (north - tiles[tile][1]) * 100.0
        #print tile, x0, xsz, y0, ysz, val[0,0]
        imgdata[y0:(y0+ysz-1),x0:(x0+xsz-1)] = val.astype('int')[:-1,:-1]
        #print imgdata[1203:1205,3858:3861], x0, y0
        nc.close()
    # Stress our color ramp
    #for i in range(256):
    #    imgdata[i*10:i*10+10,0:100] = i
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( make_colorramp() )
    png.save('q2.png')
    # Now we need to generate the world file
    o = open('/tmp/q2.wld', 'w')
    o.write("""   0.0100000000000%s
   0.00000
   0.00000
  -0.010000000000000000%.0f
%s
  %s""" % (gts.strftime("%Y%m%d%H%M"), west, north, val[1000,1000]))
    o.close()
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot a %s bogus GIS/q2/hsr_%s.wld wld' /tmp/q2.wld" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M") )
    os.system(pqstr)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/hsr.png GIS/q2/hsr_%s.png png' q2.png" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M") )
    os.system(pqstr)
    # Create 900913 image
    cmd = "/mesonet/local/bin/gdalwarp -s_srs EPSG:4326 -t_srs EPSG:900913 -q -of GTiff -tr 1000.0 1000.0 q2.png q2.tif"
    os.system( cmd )
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/q2/hsr.tif GIS/q2/hsr_%s.tif tif' q2.tif" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M") )
    os.system(pqstr)
    
    os.unlink('q2.tif')

if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])))
    else:
        gts = mx.DateTime.gmtime() - mx.DateTime.RelativeDateTime(minutes=10)
        offset = gts.minute % 5
        gts -= mx.DateTime.RelativeDateTime(minutes=offset)
        doit( gts )
