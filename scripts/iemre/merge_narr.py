"""Merge the NARR precip files to netcdf.

Unsure if I have any code that uses these .nc files, alas.

Called from dl/download_narr.py each month around the 9th.
"""
import datetime
import os
import sys

import numpy as np
import pygrib
from pyiem import iemre
from pyiem.util import ncopen, logger

LOG = logger()


def to_netcdf(valid):
    """Persist this 1 hour precip information to the netcdf storage

    Recall that this timestep has data for the previous hour"""
    fn = (
        f"/mesonet/ARCHIVE/data/{valid:%Y/%m/%d}/model/NARR/"
        f"apcp_{valid:%Y%m%d%H%M}.grib"
    )
    if not os.path.isfile(fn):
        LOG.warning("Missing file %s", fn)
        return False
    gribs = pygrib.open(fn)
    grb = gribs[1]
    val = grb.values

    tidx = int((iemre.hourly_offset(valid) + 1) / 3)
    LOG.info("%s np.min: %s np.max: %s", tidx, np.min(val), np.max(val))
    with ncopen(
        f"/mesonet/data/iemre/{valid.year}_narr.nc", "a", timeout=300
    ) as nc:
        nc.variables["apcp"][tidx, :, :] = val

    return True


def main(argv):
    """Go Main"""
    sts = datetime.datetime(int(argv[1]), int(argv[2]), 1)
    ets = (sts + datetime.timedelta(days=33)).replace(day=1)
    interval = datetime.timedelta(hours=3)
    now = sts
    while now < ets:
        to_netcdf(now)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
