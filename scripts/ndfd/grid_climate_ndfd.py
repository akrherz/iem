"""Grid climate for netcdf usage"""
import datetime

import numpy as np
import psycopg2.extras
from pyiem import iemre
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from pyiem.util import convert_value, get_dbconn, ncopen
from scipy.interpolate import NearestNDInterpolator

NT = NetworkTable([f"{abbr}CLIMATE" for abbr in state_names])
COOP = get_dbconn("coop")


def generic_gridder(nc, cursor, idx):
    """
    Generic gridding algorithm for easy variables
    """
    lats = []
    lons = []
    vals = []
    for row in cursor:
        if row[idx] is not None and row["station"] in NT.sts:
            lats.append(NT.sts[row["station"]]["lat"])
            lons.append(NT.sts[row["station"]]["lon"])
            vals.append(row[idx])
    if len(vals) < 4:
        print(
            ("Only %s observations found for %s, won't grid")
            % (len(vals), idx)
        )
        return None

    nn = NearestNDInterpolator((lons, lats), np.array(vals))
    grid = nn(nc.variables["lon"][:], nc.variables["lat"][:])
    print(
        ("%s %s %.3f %.3f")
        % (cursor.rowcount, idx, np.max(grid), np.min(grid))
    )
    if grid is not None:
        return grid
    return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    cursor = COOP.cursor(cursor_factory=psycopg2.extras.DictCursor)
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime.datetime(2000, 3, 1)

    sql = """SELECT * from climate51 WHERE valid = '%s' and
             substr(station,3,4) != '0000' and substr(station,3,1) != 'C'
             """ % (
        ts.strftime("%Y-%m-%d"),
    )
    cursor.execute(sql)
    res = generic_gridder(nc, cursor, "high")
    nc.variables["high_tmpk"][offset] = convert_value(res, "degF", "degK")

    cursor.scroll(0, mode="absolute")
    res = generic_gridder(nc, cursor, "low")
    nc.variables["low_tmpk"][offset] = convert_value(res, "degF", "degK")

    cursor.scroll(0, mode="absolute")
    res = generic_gridder(nc, cursor, "precip")
    nc.variables["p01d"][offset] = convert_value(res, "inch", "millimeter")

    cursor.scroll(0, mode="absolute")
    res = generic_gridder(nc, cursor, "gdd50")
    nc.variables["gdd50"][offset] = res


def workflow(ts):
    """our workflow"""
    # Load up a station table we are interested in

    # Load up our netcdf file!
    with ncopen("/mesonet/data/ndfd/ndfd_dailyc.nc", "a") as nc:
        grid_day(nc, ts)


def main():
    """Go Main!"""
    sts = datetime.datetime(2000, 1, 1)
    ets = datetime.datetime(2001, 1, 1)
    interval = datetime.timedelta(days=1)
    now = sts
    while now < ets:
        print(now)
        workflow(now)
        now += interval


if __name__ == "__main__":
    main()
