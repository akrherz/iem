"""Generate a composite of the MRMS PrecipRate

Within a two minute window, maybe the max rate we could see is 0.2 inches,
which is 5 mm.  So if we want to store 5mm in 250 bins, we have a resolution
of 0.02 mm per index.

"""
import datetime
import pytz
import numpy as np
import os
import tempfile
from PIL import Image
import subprocess
import json
import sys
import pyiem.mrms as mrms
import pygrib
import gzip


def do(now, realtime, delta):
    """ Generate for this timestep! """
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros((szy, szx), 'u1')
    sts = now - datetime.timedelta(minutes=2)
    metadata = {'start_valid': sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'end_valid': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                'product': 'a2m',
                'units': '0.02 mm'}

    gribfn = now.strftime(("/mnt/a4/data/%Y/%m/%d/mrms/ncep/PrecipRate/"
                           "PrecipRate_00.00_%Y%m%d-%H%M00.grib2.gz"))
    if not os.path.isfile(gribfn):
        # Don't whine about old files being missing
        if delta < 90:
            print("mrms_rainrate_comp.py MISSING %s" % (gribfn,))
        return

    # http://www.nssl.noaa.gov/projects/mrms/operational/tables.php
    # Says units are mm/hr
    fp = gzip.GzipFile(gribfn, 'rb')
    (_, tmpfn) = tempfile.mkstemp()
    tmpfp = open(tmpfn, 'wb')
    tmpfp.write(fp.read())
    tmpfp.close()
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)

    val = grb['values']
    # Convert into units of 0.1 mm accumulation
    val = val / 60.0 * 2.0 * 50.0
    val = np.where(val < 0., 255., val)
    imgdata[:, :] = np.flipud(val.astype('int'))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(mrms.make_colorramp())
    png.save('%s.png' % (tmpfn,))

    mrms.write_worldfile('%s.wld' % (tmpfn,))
    # Inject WLD file
    routes = "c" if realtime else ""
    prefix = 'a2m'
    pqstr = ("/home/ldm/bin/pqinsert -i -p 'plot a%s %s "
             "gis/images/4326/mrms/%s.wld GIS/mrms/%s_%s.wld wld' %s.wld"
             "") % (routes, now.strftime("%Y%m%d%H%M"), prefix, prefix,
                    now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = ("/home/ldm/bin/pqinsert -i -p 'plot a%s %s "
             "gis/images/4326/mrms/%s.png GIS/mrms/%s_%s.png png' %s.png"
             "") % (routes, now.strftime("%Y%m%d%H%M"), prefix, prefix,
                    now.strftime("%Y%m%d%H%M"), tmpfn)
    subprocess.call(pqstr, shell=True)

    if realtime:
        # Create 900913 image
        cmd = ("gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
               "-tr 1000.0 1000.0 %s.png %s.tif") % (tmpfn, tmpfn)
        subprocess.call(cmd, shell=True)
        # Insert into LDM
        pqstr = ("/home/ldm/bin/pqinsert -i -p 'plot c %s "
                 "gis/images/900913/mrms/%s.tif GIS/mrms/%s_%s.tif tif' %s.tif"
                 "") % (now.strftime("%Y%m%d%H%M"), prefix, prefix,
                        now.strftime("%Y%m%d%H%M"), tmpfn)
        subprocess.call(pqstr, shell=True)

        j = open("%s.json" % (tmpfn,), 'w')
        j.write(json.dumps(dict(meta=metadata)))
        j.close()
        # Insert into LDM
        pqstr = ("/home/ldm/bin/pqinsert -i -p 'plot c %s "
                 "gis/images/4326/mrms/%s.json GIS/mrms/%s_%s.json json' "
                 "%s.json") % (now.strftime("%Y%m%d%H%M"), prefix, prefix,
                               now.strftime("%Y%m%d%H%M"), tmpfn)
        subprocess.call(pqstr, shell=True)
    for suffix in ['tif', 'json', 'png', 'wld']:
        if os.path.isfile("%s.%s" % (tmpfn, suffix)):
            os.unlink('%s.%s' % (tmpfn, suffix))

    os.close(tmpfp)
    os.unlink(tmpfn)


def main():
    """ Go Main Go """
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone("UTC"))
    if len(sys.argv) == 6:
        utcnow = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                                   int(sys.argv[3]), int(sys.argv[4]),
                                   int(sys.argv[5])
                                   ).replace(tzinfo=pytz.timezone("UTC"))
        do(utcnow, False, 0)
    else:
        # If our time is an odd time, run 5 minutes ago
        utcnow = utcnow.replace(second=0, microsecond=0)
        if utcnow.minute % 2 != 1:
            return
        utcnow = utcnow - datetime.timedelta(minutes=5)
        do(utcnow, True, 0)
        # Also check old dates
        for delta in [30, 90, 1440, 2880]:
            ts = utcnow - datetime.timedelta(minutes=delta)
            fn = ts.strftime(("/mesonet/ARCHIVE/data/%Y/%m/%d/"
                              "GIS/mrms/a2m_%Y%m%d%H%M.png"))
            if not os.path.isfile(fn):
                do(ts, False, delta)

if __name__ == '__main__':
    main()
