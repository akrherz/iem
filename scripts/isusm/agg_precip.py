"""Aggregate ISUSM Precipitation.

called from RUN_5MIN.sh
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.util import get_dbconn, get_dbconnc, get_sqlalchemy_conn, logger

LOG = logger()
CST = ZoneInfo("Etc/GMT+6")


def assign_phour():
    """Due to lame reasons, IEMAcess  does not have phour set."""
    # Look in ISUAG for any phour values set
    with get_sqlalchemy_conn("isuag") as conn:
        df = pd.read_sql(
            """
            select station, iemid, valid, rain_in_tot_qc from sm_hourly h
            JOIN stations t on (h.station = t.id)
            where t.network = 'ISUSM' and
            valid >= now() - '3 hours'::interval and rain_in_tot_qc is not null
            """,
            conn,
        )
    for _, row in df.iterrows():
        pgconn, cursor = get_dbconnc("iem")
        cursor.execute(
            "UPDATE current_log SET phour = %s WHERE iemid = %s and "
            "valid = %s",
            (row["rain_in_tot_qc"], row["iemid"], row["valid"]),
        )
        LOG.info(
            "Updated %s rows for %s[%s][%s]",
            cursor.rowcount,
            row["station"],
            row["valid"],
            row["rain_in_tot_qc"],
        )
        cursor.close()
        pgconn.commit()


def main():
    """Go Main Go."""
    # Look for any precip reported
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct id, c.iemid, date(valid at time zone 'UTC+6') from "
        "current_log c JOIN stations t on "
        "(c.iemid = t.iemid) WHERE t.network = 'ISUSM' and c.pcounter > 0 and "
        "updated > now() - '10 minutes'::interval"
    )
    LOG.info("Found %s rows needing aggregation", cursor.rowcount)
    if cursor.rowcount == 0:
        return
    for station, iemid, date in cursor:
        LOG.info("Processing %s %s", station, date)
        # NB so careful here, we have to total over a CST date :(
        sts = datetime(date.year, date.month, date.day, 1, tzinfo=CST)
        ets = sts + timedelta(hours=24)

        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                """
                SELECT valid at time zone 'UTC+6' as valid, phour, pcounter
                from current_log
                WHERE iemid = %s and valid > %s and valid < %s
                ORDER by valid ASC
                """,
                conn,
                params=(iemid, sts, ets),
                index_col="valid",
            )
        if len(df.index) < 2:
            LOG.info("Skipping %s as got just %s rows", station, len(df.index))
            continue
        df = (
            df.reindex(pd.date_range(df.index[0], df.index[-1], freq="60S"))
            .fillna(0)
            .assign(
                phour=lambda df_: df_.phour.fillna(0),
                newphour=lambda df_: (
                    df_["pcounter"].rolling(60, min_periods=1).sum()
                ),
            )
        )
        # Find instances were phour != newphour
        mask = (df["phour"] - df["newphour"]).abs() > 0.001
        for valid, entry in df[mask].iterrows():
            LOG.info("Updating %s %s %s", station, valid, entry["newphour"])
            cursor2 = pgconn.cursor()
            cursor2.execute(
                "UPDATE current_log SET phour = %s WHERE iemid = %s and "
                "valid = %s",
                (entry["newphour"], iemid, valid),
            )
            cursor2.close()
            pgconn.commit()
        if mask.sum() == 0:
            continue
        # Update the pday total
        pday = df["pcounter"].sum()
        LOG.info("Updating pday %s %s %s", station, date, pday)
        cursor2 = pgconn.cursor()
        cursor2.execute(
            f"UPDATE summary_{date.year} SET pday = %s WHERE iemid = %s and "
            "day = %s",
            (pday, iemid, date),
        )
        cursor2.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
    assign_phour()
