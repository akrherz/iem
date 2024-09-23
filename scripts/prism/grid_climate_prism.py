"""Grid climate for netcdf usage"""

from datetime import datetime, timedelta
from typing import Optional

import click
import numpy as np
from pyiem import iemre
from pyiem.database import get_dbconnc
from pyiem.network import Table as NetworkTable
from pyiem.reference import state_names
from pyiem.util import convert_value, logger, ncopen
from scipy.interpolate import NearestNDInterpolator

LOG = logger()
NT = NetworkTable([f"{abbr}CLIMATE" for abbr in state_names])


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

    xi, yi = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])
    nn = NearestNDInterpolator((lons, lats), np.array(vals))
    grid = nn(xi, yi)
    LOG.info(
        "%s %s %.3f %.3f",
        cursor.rowcount,
        idx,
        np.max(grid),
        np.min(grid),
    )
    if grid is not None:
        return grid
    return None


def grid_day(nc, ts):
    """
    I proctor the gridding of data on an hourly basis
    @param ts Timestamp of the analysis, we'll consider a 20 minute window
    """
    COOP, cursor = get_dbconnc("coop")
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime(2000, 3, 1)

    sql = """SELECT * from ncei_climate91 WHERE valid = '%s' and
             substr(station,3,4) != '0000' and substr(station,3,1) != 'C'
             """ % (ts.strftime("%Y-%m-%d"),)
    cursor.execute(sql)
    if cursor.rowcount > 4:
        res = generic_gridder(nc, cursor, "high")
        if res is not None:
            nc.variables["tmax"][offset] = convert_value(res, "degF", "degC")
        cursor.scroll(0, mode="absolute")
        res = generic_gridder(nc, cursor, "low")
        if res is not None:
            nc.variables["tmin"][offset] = convert_value(res, "degF", "degC")
        cursor.scroll(0, mode="absolute")
        res = generic_gridder(nc, cursor, "precip")
        if res is not None:
            nc.variables["ppt"][offset] = convert_value(
                res, "inch", "millimeter"
            )
    else:
        print(
            ("%s has %02i entries, FAIL")
            % (ts.strftime("%Y-%m-%d"), cursor.rowcount)
        )


def workflow(ts):
    """our workflow"""
    # Load up a station table we are interested in

    # Load up our netcdf file!
    nc = ncopen("/mesonet/data/prism/prism_dailyc.nc", "a")
    grid_day(nc, ts)
    nc.close()


@click.command()
@click.option("--date", "dt", type=click.DateTime())
def main(dt: Optional[datetime]):
    """Go Main!"""
    if dt is not None:
        workflow(dt)
    else:
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
