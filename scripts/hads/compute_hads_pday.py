"""Attempt at totalling up hourly DCP data

    Run from `RUN_12Z.sh` for previous day
    Run from `RUN_20_AFTER.sh` for current day

"""
from __future__ import print_function
import datetime
import sys

import pytz
import numpy as np
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, utc


def workflow(date):
    """Do the necessary work for this date"""
    pgconn = get_dbconn("hads", user="nobody")
    iem_pgconn = get_dbconn("iem")
    icursor = iem_pgconn.cursor()
    # load up the current obs
    df = read_sql(
        """
    WITH dcp as (
        SELECT id, iemid, tzname from stations where network ~* 'DCP'
        and tzname is not null
    ), obs as (
        SELECT iemid, pday from summary_"""
        + str(date.year)
        + """
        WHERE day = %s)
    SELECT d.id, d.iemid, d.tzname, coalesce(o.pday, 0) as pday from
    dcp d LEFT JOIN obs o on (d.iemid = o.iemid)
    """,
        iem_pgconn,
        params=(date,),
        index_col="id",
    )
    bases = {}
    ts = utc(date.year, date.month, date.day, 12)
    for tzname in df["tzname"].unique():
        base = ts.astimezone(pytz.timezone(tzname))
        bases[tzname] = base.replace(hour=0)
    # retrieve data that is within 12 hours of our bounds
    sts = datetime.datetime(
        date.year, date.month, date.day
    ) - datetime.timedelta(hours=12)
    ets = sts + datetime.timedelta(hours=48)
    obsdf = read_sql(
        """
    SELECT distinct station, valid at time zone 'UTC' as utc_valid, value
    from raw"""
        + str(date.year)
        + """ WHERE valid between %s and %s and
    substr(key, 1, 3) = 'PPH' and value >= 0
    """,
        pgconn,
        params=(sts, ets),
        index_col=None,
    )
    if obsdf.empty:
        print("compute_hads_pday for %s found no data" % (date,))
        return
    obsdf["utc_valid"] = obsdf["utc_valid"].dt.tz_localize(pytz.UTC)
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
            # print("Skipping %s %s==%s" % (station, current_pday,
            #                              pday))
            continue
        # print("Updating %s old: %s new: %s" % (station, current_pday, pday))
        iemid = int(df.loc[station, "iemid"])
        icursor.execute(
            """
            UPDATE summary_"""
            + str(date.year)
            + """
            SET pday = %s WHERE iemid = %s and day = %s
        """,
            (pday, iemid, date),
        )
        if icursor.rowcount == 0:
            print("Adding record %s[%s] for day %s" % (station, iemid, date))
            icursor.execute(
                """
                INSERT into summary_"""
                + str(date.year)
                + """
                (iemid, day) VALUES (%s, %s)
            """,
                (iemid, date),
            )
            icursor.execute(
                """
                UPDATE summary_"""
                + str(date.year)
                + """
                SET pday = %s WHERE iemid = %s and day = %s
                and %s > coalesce(pday, 0)
            """,
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
