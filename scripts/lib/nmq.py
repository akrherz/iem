"""
Support the NMQ netCDF files
"""
import random
import mx.DateTime
import os
import numpy
TILES = {
         1: [-130., 55.], # 2001x1501  NW
         2: [-110., 55.], # 2001x1501  
         3: [-90., 55.],  # 1001x1501
         4: [-80., 55.],  # 2001x1501  NE
         5: [-130., 40.], # 2001x2001  SW
         6: [-110., 40.], # 2001x2001
         7: [-90., 40.],  # 1001x2001
         8: [-80., 40.]   # 2001x2001  SE
}
WEST = -130.00
NORTH = 55.00

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

def get_precip(sts, ets):
    """
    Get the precip data for a period of choice
    """
    # Expensive
    import osgeo.gdal as gdal
    # Figure out our period
    pointer = sts
    
    # Figure out which files we have available to make this work
    files = []
    for dayint in [1,1]:
        now = pointer + mx.DateTime.RelativeDateTime(days=dayint)
        while now <= ets:
            gmt = now.gmtime()
            fp = gmt.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/q2/p"+ 
                               ` 24*dayint ` +"h_%Y%m%d%H00.png")
            if os.path.isfile(fp):
                files.append( fp )
                pointer = now
            #else:
            #    mesonet.bring_me_file( fp )
            now += mx.DateTime.RelativeDateTime(days=dayint)

    if len(files) == 0:
        print 'No Data Available for Q2 monthly_total_plot.py'
        return None
    # Now we have files to loop over and add precip data too!
    total = None
    for file in files:
        img = gdal.Open(file, 0)
        data = img.ReadAsArray() # 3500, 7000 (y,x) staring upper left I think
        # Convert to mm
        precip = numpy.zeros( numpy.shape(data), 'f')
        """
         255 levels...  wanna do 0 to 20 inches
         index 255 is missing, index 0 is 0
         0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
         1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
         5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180
        """
        precip = numpy.where( numpy.logical_and(data < 255, data >= 180),
                              125.0 + ((data - 180) * 5.0), precip )
        precip = numpy.where( numpy.logical_and(data < 180, data >= 100),
                              25.0 + ((data - 100) * 1.25), precip )
        precip = numpy.where( data < 100,
                              0.0 + ((data - 0) * 0.25), precip )

        if total is None:
            total = precip
        else:
            total += precip
        del img
        
    return total

def get_image_xy(lon, lat):
    """
    Return the x, y pair for the point in the image valid for this lon, lat
    """
    x = (lon - WEST) * 100
    y = (NORTH - lat) * 100
    return x, y

def random_zeros():
    """
    Generate some number of random zeros
    """
    return "%s" % ("0" * random.randint(0, 20),)

def write_worldfile( filename ):
    """
    Write a world file to given filename
    @param filename to write the data to
    """
    output = open(filename, 'w')
    output.write("""0.010%s
0.00%s
0.00%s
-0.010%s
%s
%s""" % (random_zeros(), random_zeros(), random_zeros(), random_zeros(),
            WEST, NORTH))
    output.close()
    
def make_mosaic2d_fp(tile, gts):
    """
    Return a string for the filename expected for this timestamp
    """
    return "/mnt/a4/data/%s/nmq/tile%s/data/QPESUMS/grid/mosaic2d_nc/%s00.nc" % (
        gts.strftime("%Y/%m/%d"), tile, 
        gts.strftime("%Y%m%d-%H%M") )
