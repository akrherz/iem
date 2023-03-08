"""
Gridcell sample the ERA5Land NetCDF files to save srad to climodat database.


Run from RUN_0Z.sh for seven UTC days ago.
"""
import datetime
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
from affine import Affine
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import hourly_offset, WEST, NORTH
from pyiem.util import get_dbconn, ncopen, logger, get_sqlalchemy_conn, utc

LOG = logger()


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
    affine = Affine(0.1, 0, WEST, 0, -0.1, NORTH)
    czs = CachingZonalStats(affine)
    data = czs.gen_stats(np.flipud(rsds), gdf["geom"])
    for i, sid in enumerate(gdf.index.values):
        df.at[sid, "era5land_srad"] = data[i]


def build_stations(dt) -> pd.DataFrame:
    """Figure out what we need data for."""
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            """
            SELECT station, st_x(geom) as lon, st_y(geom) as lat, temp_hour
            from alldata a JOIN stations t on (a.station = t.id) WHERE
            t.network ~* 'CLIMATE' and a.day = %s and
            st_x(geom) between -127 and -65
            ORDER by station ASC
            """,
            conn,
            params=(dt,),
            index_col="station",
        )
    df["era5land_srad"] = np.nan
    df["i"] = np.nan
    df["j"] = np.nan
    LOG.info("Found %s database entries", len(df.index))
    return df


def compute(df, sids, dt, do_regions=False):
    """Do the magic."""
    # Life choice is to run 6z to 6z
    sts = utc(dt.year, dt.month, dt.day, 6)
    ets = sts + datetime.timedelta(hours=24)

    ncfn = f"/mesonet/data/era5/{sts.year}_era5land_hourly.nc"
    idx0 = hourly_offset(sts)
    idx1 = hourly_offset(ets)
    # Wm-2 to MJ
    factor = 3600.0 / 1_000_000.0
    with ncopen(ncfn) as nc:
        lons = nc.variables["lon"][:]
        lats = nc.variables["lat"][:]
        if f"{dt:%m%d}" == "1231":
            rsds = np.sum(nc.variables["rsds"][idx0:], 0) * factor
            ncfn2 = f"/mesonet/data/era5/{ets.year}_era5land_hourly.nc"
            with ncopen(ncfn2) as nc2:
                rsds += np.sum(nc2.variables["rsds"][:idx1], 0) * factor
        else:
            rsds = np.sum(nc.variables["rsds"][idx0:idx1], 0) * factor

    df["i"] = np.digitize(df["lon"].values, lons)
    df["j"] = np.digitize(df["lat"].values, lats)

    for sid, row in df.loc[sids].iterrows():
        df.at[sid, "era5land_srad"] = rsds[int(row["j"]), int(row["i"])]

    if do_regions:
        compute_regions(rsds, df)

    LOG.info("IA0200 %s", df.at["IA0200", "era5land_srad"])


def do(dt):
    """Process for a given date."""
    LOG.info("do(%s)", dt)
    df = build_stations(dt)
    # We currently do two options
    # 1. For morning sites 1-11 AM, they get yesterday's radiation
    sids = df[(df["temp_hour"] > 0) & (df["temp_hour"]) < 12].index.values
    compute(df, sids, dt - datetime.timedelta(days=1), True)
    # 2. All other sites get today
    sids = df[df["era5land_srad"].isna()].index.values
    compute(df, sids, dt)

    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()
    for sid, row in df[df["era5land_srad"].notna()].iterrows():
        cursor.execute(
            "UPDATE alldata set era5land_srad = %s where station = %s and "
            "day = %s",
            (row["era5land_srad"], sid, dt),
        )
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    do(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))


if __name__ == "__main__":
    main(sys.argv)
