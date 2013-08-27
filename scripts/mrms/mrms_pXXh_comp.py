'''
 Generate a composite of the MRMS XX Hour Precip total, easier than manually 
 totalling it up myself.
'''
import datetime
import pytz
import numpy as np
import os
import tempfile
import Image
import subprocess
import json
import sys
import util

def do(now, hr ):
    ''' Generate for this timestep! 
    255 levels...  wanna do 0 to 20 inches
     index 255 is missing, index 0 is 0
     0-1   -> 100 - 0.01 res ||  0 - 25   -> 100 - 0.25 mm  0
     1-5   -> 80 - 0.05 res  ||  25 - 125 ->  80 - 1.25 mm  100
     5-20  -> 75 - 0.20 res  || 125 - 500  ->  75 - 5 mm    180  
    '''
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros( (szy, szx), 'u1')
    sts = now - datetime.timedelta(hours=hr)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'product': 'lcref',
                'units': 'mm' }
    ''' 
      Loop over tiles
    Data from tile is SW corner and row , so y, x

    File represents 2 minute accumulation in 0.1 mm, so 25.4 mm
    
    So file has units of 

    '''
    for tile in range(1,5):
        fn = util.get_fn('%shrad' % (hr,), now, tile)
        if not os.path.isfile(fn):
            print "MRMS LCREF Tile: %s Time: %s UTC" % (tile, now.strftime("%Y-%m-%d %H:%M"))
            continue
        tilemeta, val = util.reader(fn)
        ''' There is currently a bug with how MRMS computes missing data :( '''
        image = np.zeros( np.shape(val), 'i')
        image = np.where(val >= 500, 254, image)
        image = np.where(np.logical_and(val >= 125, val < 500), 180 + ((val - 125.) / 5.0), image)
        image = np.where(np.logical_and(val >= 25, val < 125), 100 + ((val - 25.) / 1.25), image)
        image = np.where(np.logical_and(val >= 0, val < 25), 0 + ((val - 0.) / 0.25), image)
        image = np.where( val < 0, 255, image)
        #print tile, np.min(image), np.max(image)
        ysz, xsz = np.shape(val)
        x0 = (tilemeta['ul_lon'] - util.WEST) * 100.0
        y0 = round((tilemeta['ll_lat'] - util.SOUTH) * 100.0,0)
        imgdata[y0:(y0+ysz),x0:(x0+xsz)] = val.astype('int')

    (tmpfp, tmpfn) = tempfile.mkstemp()
    
    # Create Image
    png = Image.fromarray( np.flipud( imgdata ) )
    png.putpalette( util.make_colorramp() )
    png.save('%s.png' % (tmpfn,))

    util.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    prefix = 'p%sh' % (hr,)
    pqstr = "/home/ldm/bin/pqinsert -p 'plot ac %s gis/images/4326/mrms/%s.wld GIS/mrms/%s_%s.wld wld' %s.wld" % (
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
    if len(sys.argv) == 5:
        utcnow = datetime.datetime( int(sys.argv[1]),
                                    int(sys.argv[2]),
                                    int(sys.argv[3]),
                                    int(sys.argv[4]), 0).replace(
                                                tzinfo=pytz.timezone("UTC"))
        do( utcnow , 24)
        do( utcnow , 1)
    else:
        print 'Usage: python mrms_pXXh_comp.py YYYY MM DD HR'
        sys.exit(1)