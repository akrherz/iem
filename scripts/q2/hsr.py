"""
 Generate a raster from 8 tiles of HSR

ftp://ftp.nssl.noaa.gov/users/langston/NMQ_UPDATES/April_14_2011/NSSL_National_3D_Mosaic_April2011.pdf

"""

import numpy
import mx.DateTime
import netCDF4
from PIL import Image
import os
import sys
import random
import subprocess
import tempfile
import nmq

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
            print "q2_HSR Missing Tile: %s Time: %s" % (tile, gts)
            continue
        nc = netCDF4.Dataset( fp )
        """
        short hsr(Lat, Lon) ;
          hsr:Units = "dBZ" ;
          hsr:TypeName = "hsr" ;
          hsr:MissingData = -999.f ; # After scale factor is applied!
          hsr:Scale = 10.f ;
          hsr:attributes =  ;
        """
        val = nc.variables["hsr"][:,:] / nc.variables['hsr'].Scale
        #print val[952:957,1727:1732]

        # -99 is no return
        # -999 is missing
        # Covert to base 0 and now color index value
        val = numpy.where( val > -33., (val + 32.) * 2.0, val )
        #print val[952:957,1727:1732]

        # Missing data is color 0
        val = numpy.where( val < -990., 0., val)
        #print val[952:957,1727:1732]

        # No return is index 1
        val = numpy.where( val < 0., 1., val)
        #print "4. Min: %.2f  Avg: %.2f Max: %.2f" % (numpy.min(val), numpy.average(val),
        #                                             numpy.max(val))
        ysz, xsz = numpy.shape(val)
        x0 = (nmq.TILES[tile][0] - west) * 100.0
        y0 = (north - nmq.TILES[tile][1]) * 100.0
        #print tile, x0, xsz, y0, ysz
        #print val[952:957,1727:1732]
        imgdata[y0:(y0+ysz-1),x0:(x0+xsz-1)] = val.astype('int')[:-1,:-1]
        #print imgdata[1203:1205,3858:3861], x0, y0
        nc.close()
    # Stress our color ramp
    #for i in range(256):
    #    imgdata[i*10:i*10+10,0:100] = i
    # Create Image
    #print imgdata[2453:2455,3727:3730]
    png = Image.fromarray( imgdata )
    png.putpalette( make_colorramp() )
    sfp, tmpname = tempfile.mkstemp()
    png.save('%s.png' % (tmpname,))
    # Now we need to generate the world file
    nmq.write_worldfile('%s.wld' % (tmpname,))
    
    # Inject WLD file
    pqstr = "/home/ldm/bin/pqinsert -p 'plot a %s bogus GIS/q2/hsr_%s.wld wld' %s.wld" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M"), tmpname )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/q2/hsr.png GIS/q2/hsr_%s.png png' %s.png" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M"), tmpname )
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff -tr 1000.0 1000.0 %s.png %s.tif" % (tmpname, tmpname)
    subprocess.call( cmd , shell=True)
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/q2/hsr.tif GIS/q2/hsr_%s.tif tif' %s.tif" % (
                    gts.strftime("%Y%m%d%H%M"),gts.strftime("%Y%m%d%H%M"), tmpname )
    subprocess.call(pqstr, shell=True)
    #subprocess.call("gimp %s.png" % (tmpname,), shell=True)
    for suffix in ['tif',  'png', 'wld']:
        os.unlink('%s.%s' % (tmpname, suffix))
    os.close(sfp)
    os.unlink(tmpname)

if __name__ == "__main__":
    if len(sys.argv) == 6:
        doit(mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
                                   int(sys.argv[4]), int(sys.argv[5])))
    else:
        gts = mx.DateTime.gmtime() - mx.DateTime.RelativeDateTime(minutes=10)
        offset = gts.minute % 5
        gts -= mx.DateTime.RelativeDateTime(minutes=offset)
        doit( gts )
