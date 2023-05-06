"""Generate a composite of the MRMS PrecipRate

Within a two minute window, maybe the max rate we could see is 0.2 inches,
which is 5 mm.  So if we want to store 5mm in 250 bins, we have a resolution
of 0.02 mm per index.

"""
import datetime
import gzip
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import pygrib
from PIL import Image
from pyiem import mrms
from pyiem.util import logger, utc

LOG = logger()


def workflow(now, realtime):
    """Generate for this timestep!"""
    minutes = 2 if now.year > 2011 else 5
    szx = 7000
    szy = 3500
    # Create the image data
    imgdata = np.zeros((szy, szx), "u1")
    sts = now - datetime.timedelta(minutes=2)
    prefix = f"a{minutes}m"
    metadata = {
        "start_valid": sts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_valid": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product": prefix,
        "units": "0.02 mm",
    }

    gribfn = mrms.fetch("PrecipRate", now)
    if gribfn is None:
        lf = LOG.warning if realtime else LOG.info
        lf("Missing PrecipRate: %s", now.strftime("%Y-%m-%dT%H:%MZ"))
        return

    # http://www.nssl.noaa.gov/projects/mrms/operational/tables.php
    # Says units are mm/hr
    fp = gzip.GzipFile(gribfn, "rb")
    (_, tmpfn) = tempfile.mkstemp()
    with open(tmpfn, "wb") as fh:
        try:
            fh.write(fp.read())
        except EOFError:
            LOG.info("caught EOFError on %s, likely corrupt, deleting", gribfn)
            os.unlink(gribfn)
            return
    grbs = pygrib.open(tmpfn)
    grb = grbs[1]
    os.unlink(tmpfn)
    os.unlink(gribfn)

    val = grb["values"]
    # If has a mask, convert those to -3
    if hasattr(val, "mask"):
        val = np.where(val.mask, -3, val)
    # Convert into units of 0.02 mm accumulation
    val = val / 60.0 * minutes * 50.0
    val = np.where(val < 0.0, 255.0, val)
    imgdata[:, :] = np.flipud(val.astype("int"))

    (tmpfp, tmpfn) = tempfile.mkstemp()

    # Create Image
    png = Image.fromarray(np.flipud(imgdata))
    png.putpalette(mrms.make_colorramp())
    png.save(f"{tmpfn}.png")

    mrms.write_worldfile(f"{tmpfn}.wld")
    # Inject WLD file
    routes = "c" if realtime else ""
    pqstr = (
        f"pqinsert -i -p 'plot a{routes} {now:%Y%m%d%H%M} "
        f"gis/images/4326/mrms/{prefix}.wld GIS/mrms/{prefix}_"
        f"{now:%Y%m%d%H%M}.wld wld' {tmpfn}.wld"
    )
    subprocess.call(pqstr, shell=True)
    # Now we inject into LDM
    pqstr = (
        f"pqinsert -i -p 'plot a{routes} {now:%Y%m%d%H%M} "
        f"gis/images/4326/mrms/{prefix}.png GIS/mrms/{prefix}_"
        f"{now:%Y%m%d%H%M}.png png' {tmpfn}.png"
    )
    subprocess.call(pqstr, shell=True)

    if realtime:
        # Create 3857 image
        cmd = (
            "gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -q -of GTiff "
            f"-tr 1000.0 1000.0 {tmpfn}.png {tmpfn}.tif"
        )
        subprocess.call(cmd, shell=True)
        # Insert into LDM
        pqstr = (
            f"pqinsert -i -p 'plot c {now:%Y%m%d%H%M} "
            f"gis/images/3857/mrms/{prefix}.tif GIS/mrms/{prefix}_"
            f"{now:%Y%m%d%H%M}.tif tif' {tmpfn}.tif"
        )
        subprocess.call(pqstr, shell=True)

        with open(f"{tmpfn}.json", "w", encoding="utf8") as fh:
            fh.write(json.dumps(dict(meta=metadata)))
        # Insert into LDM
        pqstr = (
            f"pqinsert -i -p 'plot c {now:%Y%m%d%H%M} "
            f"gis/images/4326/mrms/{prefix}.json GIS/mrms/{prefix}_"
            f"{now:%Y%m%d%H%M}.json json' {tmpfn}.json"
        )
        subprocess.call(pqstr, shell=True)
    for suffix in ["tif", "json", "png", "wld"]:
        if os.path.isfile(f"{tmpfn}.{suffix}"):
            os.unlink(f"{tmpfn}.{suffix}")

    os.close(tmpfp)
    os.unlink(tmpfn)


def main(argv):
    """Go Main Go"""
    utcnow = utc()
    if len(argv) == 6:
        utcnow = utc(*[int(x) for x in argv[1:6]])
        workflow(utcnow, False)
    else:
        # If our time is an odd time, run 5 minutes ago
        utcnow = utcnow.replace(second=0, microsecond=0)
        if utcnow.minute % 2 != 1:
            return
        utcnow = utcnow - datetime.timedelta(minutes=5)
        workflow(utcnow, True)
        # Also check old dates
        for delta in [30, 90, 600, 1440, 2880]:
            ts = utcnow - datetime.timedelta(minutes=delta)
            fn = ts.strftime(
                "/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/mrms/a2m_%Y%m%d%H%M.png"
            )
            if not os.path.isfile(fn):
                workflow(ts, False)


if __name__ == "__main__":
    main(sys.argv)
