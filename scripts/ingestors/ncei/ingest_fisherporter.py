"""Ingest the Fisher/Porter rain gage data from NCEI

Run from RUN_2AM.sh for 3, 6, and 12 months in the past
on the 15th each month
"""

import datetime
import sys

import pandas as pd
from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def ingest(df, sid, cursor):
    """Process a file of data"""
    cursor.execute(
        "SELECT max(date(valid)) from hpd_alldata WHERE station = %s", (sid,)
    )
    dbmax = cursor.fetchone()[0]
    LOG.info("dbmax is %s, df.last is %s", dbmax, df.index[-1])
    if dbmax is not None:
        df = df.loc[pd.Timestamp(dbmax) :]
        cursor.execute(
            "DELETE from hpd_alldata where station = %s and valid >= %s",
            (sid, dbmax.strftime("%Y-%m-%d 00:00-0600")),
        )
        LOG.info("Removed %s rows from database", cursor.rowcount)
    LOG.info("Found %s rows to ingest", len(df.index))
    taxis = pd.date_range("2000/01/01 00:00", "2000/01/01 23:45", freq="15min")
    for date, row in df.iterrows():
        # CST
        for ts in taxis:
            valid = datetime.datetime(
                date.year, date.month, date.day, ts.hour, ts.minute
            )
            val = row[f"{ts:%H%M}Val"]
            if val < 0:  # Missing
                continue
            val = float(val) / 100.0

            cursor.execute(
                "INSERT into hpd_alldata(station, valid, precip) VALUES "
                "(%s, %s, %s)",
                (
                    sid,
                    valid.strftime("%Y-%m-%d %H:%M-0600"),
                    val,
                ),
            )
    # Update metadata
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor.execute(
        "UPDATE stations SET archive_end = %s where id = %s and "
        "network = 'IA_HPD'",
        (df.index[-1], sid),
    )
    mcursor.close()
    pgconn.commit()


def main(_argv):
    """Go Main Go"""
    nt = NetworkTable("IA_HPD")
    pgconn = get_dbconn("other")
    for sid in nt.sts:
        url = (
            "https://www.ncei.noaa.gov/pub/data/hpd/auto/v2/beta/15min/"
            f"all_csv/USC00{sid}.15m.csv"
        )
        try:
            df = pd.read_csv(
                url, low_memory=False, parse_dates=["DATE"]
            ).set_index("DATE")
        except Exception as exp:
            LOG.warning("Failed to fetch %s", url)
            LOG.exception(exp)
            continue
        cursor = pgconn.cursor()
        LOG.info(
            "Found %s rows for %s[%s-%s]",
            len(df.index),
            sid,
            df.index[0],
            df.index[-1],
        )
        ingest(df, sid, cursor)
        cursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
