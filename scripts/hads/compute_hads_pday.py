"""Attempt at totalling up DCP data

Run from `RUN_12Z.sh` for previous day
Run from `RUN_20_AFTER.sh` for current day
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger, utc
from sqlalchemy import text

LOG = logger()


def workflow(dt: date):
    """Do the necessary work for this date"""
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    # load up the current obs
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(f"""
        WITH dcp as (
            SELECT id, iemid, tzname from stations where network ~* 'DCP'
            and tzname is not null
        ), obs as (
            SELECT iemid, pday from summary_{dt:%Y}
            WHERE day = :dt)
        SELECT d.id, d.iemid, d.tzname, coalesce(o.pday, 0) as pday from
        dcp d LEFT JOIN obs o on (d.iemid = o.iemid)
        """),
            conn,
            params={"dt": dt},
            index_col="id",
        )
    bases = {}
    ts = utc(dt.year, dt.month, dt.day, 12)
    for tzname in df["tzname"].unique():
        base = ts.astimezone(ZoneInfo(tzname))
        bases[tzname] = base.replace(hour=0)
    # retrieve data that is within 12 hours of our bounds
    sts = datetime(dt.year, dt.month, dt.day) - timedelta(hours=12)
    ets = sts + timedelta(hours=48)
    with get_sqlalchemy_conn("hads") as conn:
        obsdf = pd.read_sql(
            text(f"""
        SELECT distinct station, valid at time zone 'UTC' as utc_valid, value
        from raw{dt:%Y} WHERE valid between :sts and :ets and
        substr(key, 1, 3) = 'PPH' and value >= 0
        """),
            conn,
            params={"sts": sts, "ets": ets},
            index_col=None,
        )
    if obsdf.empty:
        LOG.info("%s found no data", dt)
        return
    obsdf["utc_valid"] = obsdf["utc_valid"].dt.tz_localize(ZoneInfo("UTC"))
    precip = np.zeros((24 * 60))
    grouped = obsdf.groupby("station")
    for station in obsdf["station"].unique():
        if station not in df.index:
            continue
        precip[:] = 0
        tz = df.loc[station, "tzname"]
        current_pday = df.loc[station, "pday"]
        for _, row in grouped.get_group(station).iterrows():
            ts = row["utc_valid"].to_pydatetime()
            if ts <= bases[tz]:
                continue
            t1 = (ts - bases[tz]).total_seconds() / 60.0
            t0 = max([0, t1 - 60.0])
            precip[int(t0) : int(t1)] = row["value"] / 60.0
        pday = np.sum(precip)
        if pday > 50 or np.allclose([pday], [current_pday]):
            continue
        iemid = int(df.loc[station, "iemid"])
        icursor.execute(
            f"UPDATE summary_{dt:%Y} "
            "SET pday = %s WHERE iemid = %s and day = %s",
            (pday, iemid, dt),
        )
        if icursor.rowcount == 0:
            LOG.info("Adding record %s[%s] for day %s", station, iemid, dt)
            icursor.execute(
                f"INSERT into summary_{dt:%Y} " "(iemid, day) VALUES (%s, %s)",
                (iemid, dt),
            )
            icursor.execute(
                f"UPDATE summary_{dt:%Y} "
                "SET pday = %s WHERE iemid = %s and day = %s "
                "and %s > coalesce(pday, 0)",
                (pday, iemid, dt, pday),
            )
    icursor.close()
    iem_pgconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime())
def main(dt: datetime):
    """Do Something"""
    workflow(dt.date())


if __name__ == "__main__":
    main()
