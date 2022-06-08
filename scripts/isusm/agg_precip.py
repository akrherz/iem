"""Aggregate ISUSM Precipitation.

called from RUN_5MIN.sh
"""

import pandas as pd
from pyiem.util import get_dbconn, logger, get_sqlalchemy_conn

LOG = logger()


def main():
    """Go Main Go."""
    # Look for any precip reported
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct id, c.iemid, date(valid) from "
        "current_log c JOIN stations t on "
        "(c.iemid = t.iemid) WHERE t.network = 'ISUSM' and c.pcounter > 0 and "
        "updated > now() - '10 minutes'::interval"
    )
    LOG.info("Found %s rows needing aggregation", cursor.rowcount)
    if cursor.rowcount == 0:
        return
    for (station, iemid, date) in cursor:
        LOG.info("Processing %s %s", station, date)
        with get_sqlalchemy_conn("iem") as conn:
            df = pd.read_sql(
                "SELECT valid, phour, pcounter from current_log "
                "WHERE iemid = %s and valid >= %s and valid < %s "
                "ORDER by valid ASC",
                conn,
                params=(iemid, date, date + pd.Timedelta(days=1)),
                index_col="valid",
            )
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
