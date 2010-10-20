# Generate a GIS raster from the 8 NMQ data tiles! :)

import numpy
import mx.DateTime
import netCDF3
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
    
    # Ramp blue
    for b in range(0,37):
        c[b,2] = 255
    for b in range(37,77):
        c[b,2]= (77-b)*6
    for b in range(160,196):
        c[b,2]= (b-160)*6
    for b in range(196,256):
        c[b,2] = 254
    # Ramp Green up
    for g in range(0,37):
        c[g,1] = g*6
    for g in range(37,116):
        c[g,1] = 254
    for g in range(116,156):
        c[g,1] = (156-g)*6
    for g in range(196,256):
        c[g,1] = (g-196)*4
    # and Red
    for r in range(77,117):
        c[r,0] = (r-77)*6.
    for r in range(117,256):
        c[r,0] = 254

    # Gray for missing
    c[0,:] = [144,144,144]
    # Black to remove, eventually
    c[1,:] = [0,0,0]
    return tuple( c.ravel() )

def make_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/q2rad_hsr_nc/short_qpe/%s00.nc" % (
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
    imgdata = numpy.zeros( (szy, szx), numpy.int8)
    # Loop over tiles
    for tile in range(1,9):
        fp = make_fp(tile, gts)
        if not os.path.isfile(fp):
            print "Missing", fp
            continue
        nc = netCDF3.Dataset( fp )
        val = nc.variables["rad_hsr_1h"][:] / 10.0 # convert to mm
        # Bump up by one, so that we can set missing to color index 0
        val += 1.0
        val = numpy.where(val < 1.0, 0., val)

        ysz, xsz = numpy.shape(val)
        x0 = (tiles[tile][0] - west) * 100.0
        y0 = (north - tiles[tile][1]) * 100.0
        #print tile, x0, xsz, y0, ysz, val[0,0]
        imgdata[y0:(y0+ysz-1),x0:(x0+xsz-1)] = val.astype('int')[:-1,:-1]
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
  -0.010000000000000000
%s.000000
  %s.0000""" % (gts.strftime("%Y%m%d%H%M"), west, north))
    o.close()
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot a %s bogus GIS/q2/n1p_%s.wld wld' /tmp/q2.wld" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M") )
    os.system(pqstr)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/n1p.png GIS/q2/n1p_%s.png png' q2.png" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M") )
    os.system(pqstr)

if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])))
    else:
        gts = mx.DateTime.gmtime() - mx.DateTime.RelativeDateTime(minutes=10)
        offset = gts.minute % 5
        gts -= mx.DateTime.RelativeDateTime(minutes=offset)
        doit( gts )

    