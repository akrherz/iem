'''
Generate a composite of the MRMS RainRate
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

def do( now , realtime=False):
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
    found = False
    for tile in range(1,5):
        fn = util.get_fn('rainrate', now, tile)
        if not os.path.isfile(fn):
            if not realtime:
                print "MRMS RRate Tile: %s Time: %s UTC" % (tile, now.strftime("%Y-%m-%d %H:%M"))
            continue
        found = True
        tilemeta, val = util.reader(fn)
        # Convert into units of 0.1 mm accumulation
        val = val / 60.0 * 2.0 * 10.0
        val = np.where(val < 0., 255., val)
        ysz, xsz = np.shape(val)
        val = np.flipud(val)
        x0 = (tilemeta['ul_lon'] - util.WEST) * 100.0
        y0 = (util.NORTH - tilemeta['ul_lat']) * 100.0
        imgdata[y0:(y0+ysz),x0:(x0+xsz)] = val.astype('int')
    if not found:
        return
    (tmpfp, tmpfn) = tempfile.mkstemp()
    
    # Create Image
    png = Image.fromarray( imgdata )
    png.putpalette( util.make_colorramp() )
    png.save('%s.png' % (tmpfn,))

    util.write_worldfile('%s.wld' % (tmpfn,))
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
            do( utcnow - datetime.timedelta(minutes=3), True)
    