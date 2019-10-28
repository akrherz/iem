"""Generate a composite of the MRMS PrecipRate

Within a two minute window, maybe the max rate we could see is 0.2 inches,
which is 5 mm.  So if we want to store 5mm in 250 bins, we have a resolution
of 0.02 mm per index.

"""
from __future__ import print_function
import datetime
import os
import tempfile
import subprocess
import json
import sys
import gzip

import pytz
import numpy as np
from PIL import Image
import pyiem.mrms as mrms
import pygrib


def workflow(now, realtime):
    """ Generate for this timestep! """
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros((szy, szx), "u1")
    sts = now - datetime.timedelta(minutes=2)
    metadata = {
        "start_valid": sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_valid": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product": "a2m",
        "units": "0.02 mm",
    }

    gribfn = mrms.fetch("PrecipRate", now)
    if gribfn is None:
        print(
            ("mrms_rainrate_comp.py NODATA for PrecipRate: %s")
            % (now.strftime("%Y-%m-%dT%H:%MZ"),)
        )
        return

    # http://www.nssl.noaa.gov/projects/mrms/operational/tables.php
    # Says units are mm/hr
    fp = gzip.GzipFile(gribfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    tmpfp = open(tmpfn, "wb")
    tmpfp.write(fp.read())
    tmpfp.close()
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)
    os.unlink(gribfn)

    val = grb["values"]
    # Convert into units of 0.1 mm accumulation
    val = val / 60.0 * 2.0 * 50.0
    val = np.where(val < 0.0, 255.0, val)
    imgdata[:, :] = np.flipud(val.astype("int"))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(mrms.make_colorramp())
    png.save("%s.png" % (tmpfn,))

    mrms.write_worldfile("%s.wld" % (tmpfn,))
    # Inject WLD file
    routes = "c" if realtime else ""
    prefix = "a2m"
    pqstr = (
        "/home/ldm/bin/pqinsert -i -p 'plot a%s %s "
        "gis/images/4326/mrms/%s.wld GIS/mrms/%s_%s.wld wld' %s.wld"
        ""
    ) % (
        routes,
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = (
        "/home/ldm/bin/pqinsert -i -p 'plot a%s %s "
        "gis/images/4326/mrms/%s.png GIS/mrms/%s_%s.png png' %s.png"
        ""
    ) % (
        routes,
        now.strftime("%Y%m%d%H%M"),
        prefix,
        prefix,
        now.strftime("%Y%m%d%H%M"),
        tmpfn,
    )
    subprocess.call(pqstr, shell=True)

    if realtime:
        # Create 900913 image
        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            "-tr 1000.0 1000.0 %s.png %s.tif"
        ) % (tmpfn, tmpfn)
        subprocess.call(cmd, shell=True)
        # Insert into LDM
        pqstr = (
            "/home/ldm/bin/pqinsert -i -p 'plot c %s "
            "gis/images/900913/mrms/%s.tif GIS/mrms/%s_%s.tif tif' %s.tif"
            ""
        ) % (
            now.strftime("%Y%m%d%H%M"),
            prefix,
            prefix,
            now.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)

        j = open("%s.json" % (tmpfn,), "w")
        j.write(json.dumps(dict(meta=metadata)))
        j.close()
        # Insert into LDM
        pqstr = (
            "/home/ldm/bin/pqinsert -i -p 'plot c %s "
            "gis/images/4326/mrms/%s.json GIS/mrms/%s_%s.json json' "
            "%s.json"
        ) % (
            now.strftime("%Y%m%d%H%M"),
            prefix,
            prefix,
            now.strftime("%Y%m%d%H%M"),
            tmpfn,
        )
        subprocess.call(pqstr, shell=True)
    for suffix in ["tif", "json", "png", "wld"]:
        if os.path.isfile("%s.%s" % (tmpfn, suffix)):
            os.unlink("%s.%s" % (tmpfn, suffix))

    os.close(tmpfp)
    os.unlink(tmpfn)


def main(argv):
    """ Go Main Go """
    utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if len(argv) == 6:
        utcnow = datetime.datetime(
            int(argv[1]),
            int(argv[2]),
            int(argv[3]),
            int(argv[4]),
            int(argv[5]),
        ).replace(tzinfo=pytz.utc)
        workflow(utcnow, False)
    else:
        # If our time is an odd time, run 5 minutes ago
        utcnow = utcnow.replace(second=0, microsecond=0)
        if utcnow.minute % 2 != 1:
            return
        utcnow = utcnow - datetime.timedelta(minutes=5)
        workflow(utcnow, True)
        # Also check old dates
        for delta in [30, 90, 1440, 2880]:
            ts = utcnow - datetime.timedelta(minutes=delta)
            fn = ts.strftime(
                (
                    "/mesonet/ARCHIVE/data/%Y/%m/%d/"
                    "GIS/mrms/a2m_%Y%m%d%H%M.png"
                )
            )
            if not os.path.isfile(fn):
                workflow(ts, False)


if __name__ == "__main__":
    main(sys.argv)
