"""Attempt at totalling up DCP data

Run from `RUN_12Z.sh` for previous day
Run from `RUN_20_AFTER.sh` for current day
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import logger, utc

LOG = logger()


def workflow(dt: date):
    """Do the necessary work for this date"""
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    # load up the current obs
    with get_sqlalchemy_conn("iem") as conn:
        accessdf = pd.read_sql(
            sql_helper(
                """
        WITH dcp as (
            SELECT id, iemid, tzname from stations where network ~* 'DCP'
            and tzname is not null
        ), obs as (
            SELECT iemid, pday from {table} WHERE day = :dt)
        SELECT d.iemid, d.tzname, coalesce(o.pday, 0) as pday from
        dcp d LEFT JOIN obs o on (d.iemid = o.iemid)
        """,
                table=f"summary_{dt:%Y}",
            ),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    bases = {}
    ts = utc(dt.year, dt.month, dt.day, 12)
    for tzname in accessdf["tzname"].unique():
        base = ts.astimezone(ZoneInfo(tzname))
        bases[tzname] = base.replace(hour=0)
    # retrieve data that is within 12 hours of our bounds
    sts = datetime(dt.year, dt.month, dt.day) - timedelta(hours=12)
    ets = sts + timedelta(hours=48)
    # This brings other networks along for the ride, so be careful
    with get_sqlalchemy_conn("iem") as conn:
        obsdf = pd.read_sql(
            sql_helper(
                """
        SELECT iemid, valid at time zone 'UTC' as utc_valid, phour
        from hourly WHERE valid between :sts and :ets and phour >= 0
        order by iemid
        """
            ),
            conn,
            params={"sts": sts, "ets": ets},
            index_col=None,
        )
    if obsdf.empty:
        LOG.warning("%s found no phour access data", dt)
        return
    obsdf["utc_valid"] = obsdf["utc_valid"].dt.tz_localize(ZoneInfo("UTC"))
    counts = {
        "skips": 0,
        "updates": 0,
        "inserts": 0,
    }
    for iemid, gdf in obsdf.groupby("iemid"):
        if iemid not in accessdf.index:
            continue
        tz = accessdf.at[iemid, "tzname"]
        # obsdf stores data for the actual timestamp hour, so we want 0 to 23
        sts = bases[tz]
        ets = sts.replace(hour=23)
        current_pday = accessdf.at[iemid, "pday"]
        phour_total = gdf[
            (gdf["utc_valid"] >= sts) & (gdf["utc_valid"] <= ets)
        ]["phour"].sum()
        if phour_total > 50 or np.allclose([phour_total], [current_pday]):
            counts["skips"] += 1
            continue
        icursor.execute(
            f"UPDATE summary_{dt:%Y} "
            "SET pday = %s WHERE iemid = %s and day = %s",
            (phour_total, iemid, dt),
        )
        counts["updates"] += 1
        if icursor.rowcount == 0:
            LOG.info("Adding record %s for day %s", iemid, dt)
            icursor.execute(
                f"INSERT into summary_{dt:%Y} (iemid, day) VALUES (%s, %s)",
                (iemid, dt),
            )
            counts["inserts"] += 1
            icursor.execute(
                f"UPDATE summary_{dt:%Y} "
                "SET pday = %s WHERE iemid = %s and day = %s "
                "and %s > coalesce(pday, 0)",
                (phour_total, iemid, dt, phour_total),
            )
    icursor.close()
    iem_pgconn.commit()
    LOG.info("Counts %s", counts)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Do Something"""
    workflow(dt.date())


if __name__ == "__main__":
    main()
