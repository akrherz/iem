"""Compute the regional values.

Run from RUN_NOON.sh
"""
import datetime
import logging
import sys
import warnings

import geopandas as gpd
import numpy as np
from pyiem import iemre
from pyiem.grid.zs import CachingZonalStats
from pyiem.util import (
    convert_value,
    get_dbconn,
    get_sqlalchemy_conn,
    logger,
    mm2inch,
    ncopen,
)

LOG = logger()
LOG.setLevel(logging.INFO)
warnings.filterwarnings("ignore", category=FutureWarning)


def zero(val):
    """Make masked values a zero"""
    if val is np.ma.masked:
        return 0
    return val


def update_database(cursor, stid, valid, row):
    """Update the database with these newly computed values!"""
    if row["precip"] is None:
        LOG.info("Skipping %s as has missing data %s", stid, row)
        return
    table = f"alldata_{stid[:2]}"

    def do_update(_row):
        """Do the database work, please."""
        cursor.execute(
            f"UPDATE {table} SET high = %s, low = %s, precip = %s, snow = %s, "
            "snowd = %s, temp_hour = 7, precip_hour = 7 "
            "WHERE station = %s and day = %s",
            (
                int(round(_row["high"], 0)),
                int(round(_row["low"], 0)),
                round(zero(_row["precip"]), 2),
                round(zero(_row["snow"]), 1),
                round(zero(_row["snowd"]), 1),
                stid,
                valid,
            ),
        )
        return cursor.rowcount == 1

    if not do_update(row):
        cursor.execute(
            f"INSERT into {table} (station, day, temp_estimated, "
            "precip_estimated, year, month, sday) VALUES "
            "(%s, %s, 't', 't', %s, %s, %s)",
            (stid, valid, valid.year, valid.month, valid.strftime("%m%d")),
        )
        do_update(row)


def do_day(cursor, valid):
    """Process a day please"""
    idx = iemre.daily_offset(valid)
    with ncopen(iemre.get_daily_ncname(valid.year), "r", timeout=300) as nc:
        high = convert_value(
            nc.variables["high_tmpk_12z"][idx, :, :], "degK", "degF"
        )
        low = convert_value(
            nc.variables["low_tmpk_12z"][idx, :, :], "degK", "degF"
        )
        precip = mm2inch(nc.variables["p01d_12z"][idx, :, :])
        snow = mm2inch(nc.variables["snow_12z"][idx, :, :])
        snowd = mm2inch(nc.variables["snowd_12z"][idx, :, :])

    # get the geometries and stations to update
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
    czs = CachingZonalStats(iemre.AFFINE)
    sthigh = czs.gen_stats(np.flipud(high), gdf["geom"])
    stlow = czs.gen_stats(np.flipud(low), gdf["geom"])
    stprecip = czs.gen_stats(np.flipud(precip), gdf["geom"])
    stsnow = czs.gen_stats(np.flipud(snow), gdf["geom"])
    stsnowd = czs.gen_stats(np.flipud(snowd), gdf["geom"])

    for i, sid in enumerate(gdf.index.values):
        data = {
            "high": sthigh[i],
            "low": stlow[i],
            "precip": stprecip[i],
            "snow": stsnow[i],
            "snowd": stsnowd[i],
        }
        update_database(cursor, sid, valid, data)


def main(argv):
    """Go Main Go"""
    conn = get_dbconn("coop")
    cursor = conn.cursor()
    do_day(cursor, datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))
    cursor.close()
    conn.commit()


if __name__ == "__main__":
    main(sys.argv)
