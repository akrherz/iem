"""Merge the NARR precip files to netcdf"""
import datetime
import os
import sys

import numpy as np
import pygrib
from pyiem import iemre
from pyiem.util import ncopen


def to_netcdf(valid):
    """Persist this 1 hour precip information to the netcdf storage

    Recall that this timestep has data for the previous hour"""
    fn = ("/mesonet/ARCHIVE/data/%s/model/NARR/apcp_%s.grib") % (
        valid.strftime("%Y/%m/%d"),
        valid.strftime("%Y%m%d%H%M"),
    )
    if not os.path.isfile(fn):
        print("merge_narr: missing file %s" % (fn,))
        return False
    gribs = pygrib.open(fn)
    grb = gribs[1]
    val = grb.values

    nc = ncopen(
        "/mesonet/data/iemre/%s_narr.nc" % (valid.year,), "a", timeout=300
    )
    tidx = int((iemre.hourly_offset(valid) + 1) / 3)
    print("%s np.min: %s np.max: %s" % (tidx, np.min(val), np.max(val)))
    apcp = nc.variables["apcp"]
    apcp[tidx, :, :] = val
    nc.close()

    return True


def main(argv):
    """Go Main"""
    year = int(argv[1])
    sts = datetime.datetime(year, 1, 1)
    ets = datetime.datetime(year + 1, 1, 1)
    interval = datetime.timedelta(hours=3)
    now = sts
    while now < ets:
        to_netcdf(now)
        now += interval


if __name__ == "__main__":
    main(sys.argv)
