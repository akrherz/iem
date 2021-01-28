"""Grid climate for netcdf usage"""
import sys
import datetime

import numpy as np
from pandas.io.sql import read_sql
from scipy.interpolate import NearestNDInterpolator
from pyiem import iemre
from pyiem.util import get_dbconn, ncopen, convert_value


def generic_gridder(nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    xi, yi = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])
    nn = NearestNDInterpolator(
        (df["lon"].values, df["lat"].values), df[idx].values
    )
    grid = nn(xi, yi)
    print(
        ("%s %s %.3f %.3f") % (len(df.index), idx, np.max(grid), np.min(grid))
    )
    if grid is not None:
        return grid
    return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis

    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    pgconn = get_dbconn("coop")
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime.datetime(2000, 3, 1)

    df = read_sql(
        """
        SELECT c.*, st_x(t.geom) as lon, st_y(t.geom) as lat
        from ncdc_climate71 c JOIN stations t ON (c.station = t.id)
        WHERE valid = %s and
        substr(station,3,4) != '0000' and substr(station,3,1) != 'C'
    """,
        pgconn,
        params=(ts,),
        index_col="station",
    )
    if len(df.index) > 4:
        if "high_tmpk" in nc.variables:
            res = generic_gridder(nc, df, "high")
            if res is not None:
                nc.variables["high_tmpk"][offset] = convert_value(
                    res, "degF", "degK"
                )
            res = generic_gridder(nc, df, "low")
            if res is not None:
                nc.variables["low_tmpk"][offset] = convert_value(
                    res, "degF", "degK"
                )
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
    """Do Work"""

    # Load up our netcdf file!
    nc = ncopen(iemre.get_dailyc_ncname(), "a", timeout=300)
    grid_day(nc, ts)
    nc.close()

    nc = ncopen(iemre.get_dailyc_mrms_ncname(), "a", timeout=300)
    grid_day(nc, ts)
    nc.close()


def main(argv):
    """Go Main!"""
    if len(argv) == 4:
        ts = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]))
        workflow(ts)
    else:
        sts = datetime.datetime(2000, 1, 1)
        ets = datetime.datetime(2001, 1, 1)
        interval = datetime.timedelta(days=1)
        now = sts
        while now < ets:
            print(now)
            workflow(now)
            now += interval


if __name__ == "__main__":
    main(sys.argv)
