'''
Generate a composite of the MRMS RainRate
'''
import datetime
import pytz
import struct
import numpy as np
import gzip 
import os
import tempfile
import random
import Image
import subprocess
import json
import sys

WEST = -130.
NORTH = 55.

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
    unit = struct.unpack('6c', fp.read(6))
    var_scale, miss_val, num_radars = struct.unpack('3i', fp.read(12))
    rad_list = struct.unpack('%sc' % (num_radars*4,), fp.read(num_radars*4))
    
    sz = nx * ny * nz
    data = struct.unpack('%sh' % (sz,), fp.read(sz*2))
    data = np.reshape(np.array(data), (ny,nx)) / float(var_scale)
    #ma.masked_equal(data, miss_val)
    #print nx, ny, nz, levels, rad_list, len(data), data[1000], var_scale
    #print miss_val, np.shape(data)
    
    fp.close()
    return metadata, data

def get_fn( now, tile):
    ''' Get the filename for this timestamp and tile '''
    return now.strftime(('/mnt/mtarchive/data/%Y/%m/%d/mrms/tile'+str(tile)+
                         '/rainrate/rainrate.%Y%m%d.%H%M00.gz'))

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


def do( now ):
    ''' Generate for this timestep! '''
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros( (szy, szx), 'u1')
    sts = now - datetime.timedelta(minutes=2)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'product': 'a2m',
                'units': '0.1 mm' }
    ''' 
      Loop over tiles
    Data from tile is SW corner and row , so y, x

    File represents 2 minute accumulation in 0.1 mm, so 25.4 mm
    
    So file has units of 

    '''
    for tile in range(1,5):
        fn = get_fn(now, tile)
        if not os.path.isfile(fn):
            print "MRMS RRate Tile: %s Time: %s UTC" % (tile, now.strftime("%Y-%m-%d %H:%M"))
            continue
        tilemeta, val = reader(fn)
        # Convert into units of 0.1 mm accumulation
        val = val / 60.0 * 2.0 * 10.0
        val = np.where(val < 0., 255., val)
        ysz, xsz = np.shape(val)
        val = np.flipud(val)
        x0 = (tilemeta['ul_lon'] - WEST) * 100.0
        y0 = (NORTH - tilemeta['ul_lat']) * 100.0
        imgdata[y0:(y0+ysz),x0:(x0+xsz)] = val.astype('int')

    (tmpfp, tmpfn) = tempfile.mkstemp()
    
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( make_colorramp() )
    png.save('%s.png' % (tmpfn,))

    write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    prefix = 'a2m'
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/mrms/%s.wld GIS/mrmq/%s_%s.wld wld' %s.wld" % (
                    now.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    now.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/mrms/%s.png GIS/mrms/%s_%s.png png' %s.png" % (
                    now.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    now.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    # Create 900913 image
    cmd = "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff -tr 1000.0 1000.0 %s.png %s.tif" % (tmpfn, tmpfn)
    subprocess.call(cmd, shell=True)
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/900913/mrms/%s.tif GIS/mrms/%s_%s.tif tif' %s.tif" % (
                    now.strftime("%Y%m%d%H%M"), prefix, prefix, 
                    now.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    
    j = open("%s.json" % (tmpfn,), 'w')
    j.write( json.dumps(dict(meta=metadata)))
    j.close()
    # Insert into LDM
    pqstr = "/home/ldm/bin/pqinsert -p 'plot c %s gis/images/4326/mrms/%s.json GIS/mrms/%s_%s.json json' %s.json" % (
                    now.strftime("%Y%m%d%H%M"),prefix, prefix, now.strftime("%Y%m%d%H%M"), tmpfn )
    subprocess.call(pqstr, shell=True)
    for suffix in ['tif', 'json', 'png', 'wld']:
        os.unlink('%s.%s' % (tmpfn, suffix))

    os.close(tmpfp)
    os.unlink(tmpfn)


if __name__ == '__main__':
    ''' Lets do something '''
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
    if len(sys.argv) == 6:
        utcnow = datetime.datetime( int(sys.argv[1]),
                                    int(sys.argv[2]),
                                    int(sys.argv[3]),
                                    int(sys.argv[4]),
                                    int(sys.argv[5]) ).replace(
                                                tzinfo=pytz.timezone("UTC"))
        do( utcnow )
    else:
        ''' If our time is an odd time, run 3 minutes ago '''
        utcnow = utcnow.replace(second=0,microsecond=0)
        if utcnow.minute % 2 == 1:
            do( utcnow - datetime.timedelta(minutes=3))
    