"""
Support the NMQ netCDF files
"""
import random

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

def random_zeros():
    """
    Generate some number of random zeros
    """
    return "%s" % ("0" * random.randint(0, 10),)

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