'''
 Util functions for MRMS data, will move to pyIEM eventually
'''
import random
import numpy as np
import struct
import datetime
import pytz
import gzip

WEST = -130.
EAST = -60.
NORTH = 55.
SOUTH = 20.
XAXIS = np.arange(WEST, EAST, 0.01)
YAXIS = np.arange(SOUTH, NORTH, 0.01)

def make_colorramp():
    """
    Make me a crude color ramp
    """
    c = np.zeros((256,3), np.int)

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
    c[255,:] = [144,144,144]
    # Black to remove, eventually
    c[0,:] = [0,0,0]
    return tuple( c.ravel() )



def reader(fn):
    ''' Return metadata and the data '''
    fp = gzip.open(fn, 'rb')
    metadata = {}
    (year, month, day, hour, minute, second, nx, ny, nz, b,b,b,b,
     scale, b,b,b, ul_lon_cc, ul_lat_cc, b, scale_lon, scale_lat,
     grid_scale) = struct.unpack('9i4c10i', fp.read(80))

    metadata['ul_lon'] = ul_lon_cc / float(scale_lon) - 0.005
    metadata['ul_lat'] = ul_lat_cc / float(scale_lat) + 0.005
    metadata['valid'] = datetime.datetime(year, month, day, hour, minute,
                                second).replace(tzinfo=pytz.timezone("UTC"))

    levels = struct.unpack('%si' % (nz,), fp.read(nz*4))
    z_scale = struct.unpack('i', fp.read(4))
    bogus = struct.unpack('10i', fp.read(40))
    varname = struct.unpack('20c', fp.read(20))
    metadata['unit'] = struct.unpack('6c', fp.read(6))
    var_scale, miss_val, num_radars = struct.unpack('3i', fp.read(12))
    rad_list = struct.unpack('%sc' % (num_radars*4,), fp.read(num_radars*4))
    #print unit, var_scale, miss_val
    sz = nx * ny * nz
    data = struct.unpack('%sh' % (sz,), fp.read(sz*2))
    data = np.reshape(np.array(data), (ny,nx)) / float(var_scale)
    #ma.masked_equal(data, miss_val)
    #print nx, ny, nz, levels, rad_list, len(data), data[1000], var_scale
    #print miss_val, np.shape(data)
    
    fp.close()
    return metadata, data

def get_fn(prefix, now, tile):
    ''' Get the filename for this timestamp and tile '''
    return now.strftime(('/mnt/a4/data/%Y/%m/%d/mrms/tile'+str(tile)+
                         '/'+prefix+'/'+prefix+'.%Y%m%d.%H%M00.gz'))

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