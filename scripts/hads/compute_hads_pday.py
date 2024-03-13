"""Attempt at totalling up DCP data

Run from `RUN_12Z.sh` for previous day
Run from `RUN_20_AFTER.sh` for current day
"""

import datetime
import sys
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import logger, utc

LOG = logger()


def workflow(date):
    """Do the necessary work for this date"""
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    # load up the current obs
    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            f"""
        WITH dcp as (
            SELECT id, iemid, tzname from stations where network ~* 'DCP'
            and tzname is not null
        ), obs as (
            SELECT iemid, pday from summary_{date.year}
            WHERE day = %s)
        SELECT d.id, d.iemid, d.tzname, coalesce(o.pday, 0) as pday from
        dcp d LEFT JOIN obs o on (d.iemid = o.iemid)
        """,
            conn,
            params=(date,),
            index_col="id",
        )
    bases = {}
    ts = utc(date.year, date.month, date.day, 12)
    for tzname in df["tzname"].unique():
        base = ts.astimezone(ZoneInfo(tzname))
        bases[tzname] = base.replace(hour=0)
    # retrieve data that is within 12 hours of our bounds
    sts = datetime.datetime(
        date.year, date.month, date.day
    ) - datetime.timedelta(hours=12)
    ets = sts + datetime.timedelta(hours=48)
    with get_sqlalchemy_conn("hads") as conn:
        obsdf = pd.read_sql(
            f"""
        SELECT distinct station, valid at time zone 'UTC' as utc_valid, value
        from raw{date.year} WHERE valid between %s and %s and
        substr(key, 1, 3) = 'PPH' and value >= 0
        """,
            conn,
            params=(sts, ets),
            index_col=None,
        )
    if obsdf.empty:
        LOG.info("%s found no data", date)
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
            f"UPDATE summary_{date.year} "
            "SET pday = %s WHERE iemid = %s and day = %s",
            (pday, iemid, date),
        )
        if icursor.rowcount == 0:
            LOG.info("Adding record %s[%s] for day %s", station, iemid, date)
            icursor.execute(
                f"INSERT into summary_{date.year} "
                "(iemid, day) VALUES (%s, %s)",
                (iemid, date),
            )
            icursor.execute(
                f"UPDATE summary_{date.year} "
                "SET pday = %s WHERE iemid = %s and day = %s "
                "and %s > coalesce(pday, 0)",
                (pday, iemid, date, pday),
            )
    icursor.close()
    iem_pgconn.commit()


def main(argv):
    """Do Something"""
    if len(argv) == 4:
        ts = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        ts = datetime.date.today()
    workflow(ts)


if __name__ == "__main__":
    main(sys.argv)
