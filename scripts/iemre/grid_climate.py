"""Grid climate for netcdf usage"""

import sys
from datetime import datetime
from typing import Optional

import click
import numpy as np
import pandas as pd
from pyiem import iemre
from pyiem.database import get_sqlalchemy_conn
from pyiem.util import convert_value, logger, ncopen
from scipy.interpolate import NearestNDInterpolator
from sqlalchemy import text

LOG = logger()


def generic_gridder(nc, df, idx):
    """
    Generic gridding algorithm for easy variables
    """
    xi, yi = np.meshgrid(nc.variables["lon"][:], nc.variables["lat"][:])
    nn = NearestNDInterpolator(
        (df["lon"].values, df["lat"].values), df[idx].values
    )
    grid = nn(xi, yi)
    LOG.info(
        "%s %s %.3f %.3f",
        len(df.index),
        idx,
        np.max(grid),
        np.min(grid),
    )
    if grid is not None:
        return grid
    return None


def grid_solar(nc, ts):
    """Special Solar Ops."""
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime(2000, 3, 1)

    with get_sqlalchemy_conn("coop") as conn:
        # Look for stations with data back to 1979 for merra
        df = pd.read_sql(
            text(
                """
            with data as (
                select station, count(*), avg(merra_srad) from alldata
                where sday = :sday and merra_srad is not null
                GROUP by station
            )
            SELECT d.avg as rad, st_x(t.geom) as lon, st_y(t.geom) as lat,
            station from data d JOIN stations t ON (d.station = t.id)
            WHERE count >= :minyears
        """
            ),
            conn,
            params={
                "sday": ts.strftime("%m%d"),
                "minyears": (2020 - 1979),  # approx
            },
            index_col="station",
        )
    # Database storage is MJ, so is our netcdf
    nc.variables["swdn"][offset] = generic_gridder(nc, df, "rad")


def grid_day(nc, ts):
    """Grid things."""
    offset = iemre.daily_offset(ts)
    if ts.day == 29 and ts.month == 2:
        ts = datetime(2000, 3, 1)

    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT c.*, st_x(t.geom) as lon, st_y(t.geom) as lat
            from ncei_climate91 c JOIN stations t ON (c.station = t.id)
            WHERE valid = %s
        """,
            conn,
            params=(ts,),
            index_col="station",
        )
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
        nc.variables["p01d"][offset] = convert_value(res, "inch", "millimeter")


def workflow(ts):
    """Do Work"""

    # Load up our netcdf file!
    with ncopen(iemre.get_dailyc_ncname(domain=""), "a", timeout=300) as nc:
        grid_day(nc, ts)
        grid_solar(nc, ts)

    with ncopen(iemre.get_dailyc_mrms_ncname(), "a", timeout=300) as nc:
        grid_day(nc, ts)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Specific date")
def main(dt: Optional[datetime]):
    """Go Main!"""
    if dt:
        workflow(dt)
    else:
        for ts in pd.date_range("2000/1/1", "2000/12/31"):
            LOG.info(ts)
            workflow(ts)


if __name__ == "__main__":
    main(sys.argv)
