"""
Sample the MERRA solar radiation analysis into estimated values for the
COOP point archive

1 langley is 41840.00 J m-2 is 41840.00 W s m-2 is 11.622 W hr m-2

So 1000 W m-2 x 3600 is 3,600,000 W s m-2 is 86 langleys

RUN_MIDNIGHT.sh every 28th of the month.
"""
import datetime
import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from affine import Affine
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import logger, ncopen

LOG = logger()
COL = "merra_srad"


def compute_regions(rsds, df):
    """Do the spatial averaging work."""
    with get_sqlalchemy_conn("coop") as conn:
        gdf = gpd.read_postgis(
            """
            SELECT t.id, c.geom from stations t JOIN climodat_regions c on
            (t.iemid = c.iemid) ORDER by t.id ASC
            """,
            conn,
            index_col="id",
            geom_col="geom",
        )
    affine = Affine(0.625, 0, -180.0, 0, -0.5, 90)
    czs = CachingZonalStats(affine)
    data = czs.gen_stats(np.flipud(rsds), gdf["geom"])
    for i, sid in enumerate(gdf.index.values):
        df.at[sid, COL] = data[i]


def get_gp(xc, yc, x, y):
    """Return the grid point closest to this point"""
    distance = []
    xidx = (np.abs(xc - x)).argmin()
    yidx = (np.abs(yc - y)).argmin()
    dx = x - xc[xidx]
    dy = y - yc[yidx]
    if abs(dx) > 1 or abs(dy) > 1:
        return None, None, None
    movex = -1
    if dx >= 0:
        movex = 1
    movey = -1
    if dy >= 0:
        movey = 1
    gridx = [xidx, xidx + movex, xidx + movex, xidx]
    gridy = [yidx, yidx, yidx + movey, yidx + movey]
    for myx, myy in zip(gridx, gridy):
        d = ((y - yc[myy]) ** 2 + (x - xc[myx]) ** 2) ** 0.5
        distance.append(d)
    return gridx, gridy, distance


def build_stations(dt) -> pd.DataFrame:
    """Figure out what we need data for."""
    with get_sqlalchemy_conn("coop") as conn:
        # There's a lone VICLIMATE site at -65 :/
        df = pd.read_sql(
            """
            SELECT station, st_x(geom) as lon, st_y(geom) as lat, temp_hour
            from alldata a JOIN stations t on (a.station = t.id) WHERE
            t.network ~* 'CLIMATE' and a.day = %s and
            st_y(geom) > 0
            ORDER by station ASC
            """,
            conn,
            params=(dt,),
            index_col="station",
        )
    df[COL] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt, do_regions=False):
    """Compute things."""
    sts = dt.replace(hour=6)  # 6z
    ets = sts + datetime.timedelta(days=1)
    fn = sts.strftime("/mesonet/data/merra2/%Y/%Y%m%d.nc")
    fn2 = ets.strftime("/mesonet/data/merra2/%Y/%Y%m%d.nc")
    if not os.path.isfile(fn):
        LOG.warning("%s miss[%s] -> fail", sts.strftime("%Y%m%d"), fn)
        return
    with ncopen(fn, timeout=300) as nc:
        rad = np.sum(nc.variables["SWGDN"][7:, :, :], 0)
        xc = nc.variables["lon"][:]
        yc = nc.variables["lat"][:]

    if not os.path.isfile(fn2):
        LOG.warning("%s miss[%s] -> zeros", sts.strftime("%Y%m%d"), fn2)
        rad2 = 0
    else:
        with ncopen(fn2, timeout=300) as nc:
            rad2 = np.sum(nc.variables["SWGDN"][:7, :, :], 0)

    # W m-2 -> J m-2 s-1 -> J m-2 dy-1 -> MJ m-2 dy-1
    total = (rad + rad2) * 3600.0 / 1_000_000.0

    for sid, row in df.loc[sids].iterrows():
        (gridxs, gridys, distances) = get_gp(xc, yc, row["lon"], row["lat"])

        z0 = total[gridys[0], gridxs[0]]
        z1 = total[gridys[1], gridxs[1]]
        z2 = total[gridys[2], gridxs[2]]
        z3 = total[gridys[3], gridxs[3]]

        val = (
            z0 / distances[0]
            + z1 / distances[1]
            + z2 / distances[2]
            + z3 / distances[3]
        ) / (
            1.0 / distances[0]
            + 1.0 / distances[1]
            + 1.0 / distances[2]
            + 1.0 / distances[3]
        )
        # MJ m-2 dy-1
        df.at[sid, COL] = float(val)
    if do_regions:
        compute_regions(total, df)


def do(dt):
    """Process for a given date."""
    LOG.info("do(%s)", dt)
    df = build_stations(dt)
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's radiation
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"] < 12)].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df[COL].isna()].index.values
    compute(df, sids, dt)

    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    for sid, row in df[df[COL].notna()].iterrows():
        cursor.execute(
            f"UPDATE alldata set {COL} = %s where station = %s and "
            "day = %s",
            (row[COL], sid, dt),
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


def main(argv):
    """Go Main Go"""
    if len(argv) == 4:
        do(datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3])))
    if len(argv) == 3:
        # Run for a given month!
        sts = datetime.datetime(int(argv[1]), int(argv[2]), 1)
        # run for last date of previous month as well
        sts = sts - datetime.timedelta(days=1)
        ets = sts + datetime.timedelta(days=45)
        ets = ets.replace(day=1)
        now = sts
        while now < ets:
            do(now)
            now += datetime.timedelta(days=1)


if __name__ == "__main__":
    main(sys.argv)
