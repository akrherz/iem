"""Merge the 0.01x0.01 Q3 24 hour precip data estimates.

called from RUN_10_AFTER.sh
"""
import datetime
import gzip
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

import numpy as np
import pygrib
from pyiem import iemre, mrms
from pyiem.util import logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"


def run(ts):
    """Update netcdf file with the MRMS data

    Args:
      ts (datetime): timestamptz at midnight central time and we are running
        forward in time
    """
    nc = ncopen(iemre.get_daily_mrms_ncname(ts.year), "a", timeout=300)
    offset = iemre.daily_offset(ts)
    ncprecip = nc.variables["p01d"]

    gmtts = ts.astimezone(ZoneInfo("UTC"))
    utcnow = utc()
    total = None
    lats = None
    for _ in range(1, 25):
        gmtts += datetime.timedelta(hours=1)
        if gmtts > utcnow:
            continue
        gribfn = None
        for prefix in ["MultiSensor_QPE_01H_Pass2", "RadarOnly_QPE_01H"]:
            fn = mrms.fetch(prefix, gmtts)
            if fn is None:
                continue
            (_, gribfn) = tempfile.mkstemp()
            with gzip.GzipFile(fn, "rb") as zfn, open(gribfn, "wb") as tmpfp:
                tmpfp.write(zfn.read())
            os.unlink(fn)
            break
        if gribfn is None:
            if gmtts < utcnow:
                LOG.info("MISSING %s", gmtts)
            continue
        grbs = pygrib.open(gribfn)
        grb = grbs[1]
        if lats is None:
            lats, _ = grb.latlons()
        os.unlink(gribfn)

        val = grb["values"]
        # Anything less than zero, we set to zero
        val = np.where(val < 0, 0, val)
        if total is None:
            total = val
        else:
            total += val

    if lats is None:
        LOG.warning("nodata for %s, using zeros", ts.date())
        ncprecip[offset, :, :] = 0
        nc.close()
        return
    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    y0 = int((lats[0, 0] - iemre.NORTH) * 100.0)
    y1 = int((lats[0, 0] - iemre.SOUTH) * 100.0)
    x0 = int((iemre.WEST - mrms.WEST) * 100.0)
    x1 = int((iemre.EAST - mrms.WEST) * 100.0)
    # print(('y0:%s y1:%s x0:%s x1:%s lat0:%s offset:%s '
    #       ) % (y0, y1, x0, x1, lats[0, 0], offset))
    ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])
    nc.close()


def main(argv):
    """go main go"""
    if len(argv) == 4:
        # 12 noon to prevent ugliness with timezones
        ts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 12, 0)
    else:
        # default to noon today
        ts = datetime.datetime.now()
        ts = ts.replace(hour=12)

    ts = ts.replace(tzinfo=ZoneInfo("UTC"))
    ts = ts.astimezone(ZoneInfo("America/Chicago"))
    ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    run(ts)


if __name__ == "__main__":
    main(sys.argv)
