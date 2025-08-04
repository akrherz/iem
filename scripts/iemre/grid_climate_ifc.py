"""Grid climate for netcdf usage"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pyiem import iemre
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import convert_value, logger, ncopen
from scipy.interpolate import NearestNDInterpolator

LOG = logger()


def generic_gridder(nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    xi, yi = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])
    nn = NearestNDInterpolator(
        (df["lon"].values, df["lat"].values),
        df["precip"].values,
    )
    grid = nn(xi, yi)
    LOG.info(
        "%s %s grid:%.3f->%.3f obs:%.2f->%.2f",
        len(df.index),
        idx,
        np.min(grid),
        np.max(grid),
        df[idx].min(),
        df[idx].max(),
    )
    if grid is not None:
        return grid
    return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime(2000, 3, 1)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            "select station, st_x(geom) as lon, st_y(geom) as lat, precip "
            "from ncei_climate91 c JOIN stations t on (c.station = t.id) "
            "WHERE t.network = 'NCEI91' and c.valid = %s",
            conn,
            params=(ts.strftime("%Y-%m-%d"),),
            index_col="station",
        )
    if len(df.index) > 4:
        res = generic_gridder(nc, df, "precip")
        if res is not None:
            nc.variables["p01d"][offset] = convert_value(
                res, "inch", "millimeter"
            )
    else:
        print(
            ("%s has %02i entries, FAIL")
            % (ts.strftime("%Y-%m-%d"), len(df.index))
        )


def workflow(ts):
    """our workflow"""
    # Load up our netcdf file!
    with ncopen("/mesonet/data/iemre/ifc_dailyc.nc", "a") as nc:
        grid_day(nc, ts)


def main():
    """Go Main!"""
    sts = datetime(2000, 1, 1)
    ets = datetime(2001, 1, 1)
    interval = timedelta(days=1)
    now = sts
    while now < ets:
        print(now)
        workflow(now)
        now += interval


if __name__ == "__main__":
    main()
