"""Compute the regional values.

For non-PRISM periods, we use the IEMRE analysis.  A crude check found PRISM
to agree much better with the official data at NCEI than what my clunky routine
was doing.

Run from RUN_NOON.sh
"""

from datetime import date, datetime

import click
import geopandas as gpd
import numpy as np
from pyiem.database import get_dbconnc, get_sqlalchemy_conn, sql_helper
from pyiem.grid.nav import get_nav
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import daily_offset, get_daily_ncname
from pyiem.util import convert_value, logger, mm2inch, ncopen

LOG = logger()


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
    LOG.info(
        "%s hi:%3.0f lo:%3.0f precip:%.2f snow:%3.1f snowd:%3.1f",
        stid,
        row["high"],
        row["low"],
        row["precip"],
        round(zero(row["snow"]), 1),
        round(zero(row["snowd"]), 1),
    )

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


def do_day(cursor, valid: date):
    """Process a day please"""
    idx = daily_offset(valid)
    with ncopen(get_daily_ncname(valid.year), "r", timeout=300) as nc:
        snow = mm2inch(nc.variables["snow_12z"][idx])
        snowd = mm2inch(nc.variables["snowd_12z"][idx])
    if valid.year < 1981 or (date.today() - valid).days < 4:
        tp_nav = get_nav("iemre", "")
        ncfn = get_daily_ncname(valid.year)
        with ncopen(ncfn) as nc:
            high = convert_value(
                nc.variables["high_tmpk_12z"][idx], "degK", "degF"
            )
            low = convert_value(
                nc.variables["low_tmpk_12z"][idx], "degK", "degF"
            )
            precip = mm2inch(nc.variables["p01d_12z"][idx])
    else:
        tp_nav = get_nav("PRISM", "")
        ncfn = f"/mesonet/data/prism/{valid:%Y}_daily.nc"
        with ncopen(ncfn) as nc:
            high = convert_value(nc.variables["tmax"][idx], "degC", "degF")
            low = convert_value(nc.variables["tmin"][idx], "degC", "degF")
            precip = mm2inch(nc.variables["ppt"][idx])
    LOG.info("Used %s for hi,lo,pcp", ncfn)

    # get the geometries and stations to update
    with get_sqlalchemy_conn("coop") as conn:
        gdf = gpd.read_postgis(
            sql_helper("""
            SELECT t.id, c.geom from stations t JOIN climodat_regions c on
            (t.iemid = c.iemid) ORDER by t.id ASC
            """),
            conn,
            index_col="id",
            geom_col="geom",
        )  # type: ignore
    czs = CachingZonalStats(get_nav("iemre", "").affine_image)
    stsnow = czs.gen_stats(np.flipud(snow), gdf["geom"])
    stsnowd = czs.gen_stats(np.flipud(snowd), gdf["geom"])
    czs = CachingZonalStats(tp_nav.affine_image)
    sthigh = czs.gen_stats(np.flipud(high), gdf["geom"])
    stlow = czs.gen_stats(np.flipud(low), gdf["geom"])
    stprecip = czs.gen_stats(np.flipud(precip), gdf["geom"])

    for i, sid in enumerate(gdf.index.values):
        data = {
            "high": sthigh[i],
            "low": stlow[i],
            "precip": stprecip[i],
            "snow": stsnow[i],
            "snowd": stsnowd[i],
        }
        update_database(cursor, sid, valid, data)


@click.command()
@click.option(
    "--date",
    "dt",
    required=True,
    type=click.DateTime(),
    help="Date to process",
)
def main(dt: datetime):
    """Go Main Go"""
    conn, cursor = get_dbconnc("coop")
    do_day(cursor, dt.date())
    cursor.close()
    conn.commit()


if __name__ == "__main__":
    main()
