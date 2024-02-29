"""Backfill IEMAccess Summary table.

Some of the variables don't get properly updated in the summary table.

cronjob from RUN_2AM.sh
"""

import sys
from datetime import timedelta

import pandas as pd
from pyiem.util import get_dbconn, get_sqlalchemy_conn, logger, utc

LOG = logger()


def process(pgconn, obs):
    """option 1"""
    rcursor = pgconn.cursor()
    wcursor = pgconn.cursor()
    done = 0
    for _, row in obs.iterrows():
        rcursor.execute(
            "SELECT avg_rh from summary where iemid = %s and day = %s",
            (row["iemid"], row["valid"]),
        )
        if rcursor.rowcount == 0:
            LOG.warning("No summary row for %s %s", row["iemid"], row["valid"])
            continue
        rh_avg = rcursor.fetchone()[0]
        if rh_avg is not None and abs(rh_avg - row["rh_avg_qc"]) < 1:
            continue
        done += 1
        if done % 100 == 0:
            LOG.info("Cycling cursor")
            wcursor.close()
            pgconn.commit()
            wcursor = pgconn.cursor()

        wcursor.execute(
            "UPDATE summary SET avg_rh = %s WHERE iemid = %s and day = %s",
            (row["rh_avg_qc"], row["iemid"], row["valid"]),
        )
    LOG.info("Did %s updates of summary table", done)
    if wcursor is not None:
        wcursor.close()
        pgconn.commit()


def main(argv):
    """Go Main Go"""
    fullreprocess = len(argv) > 1 and argv[1] == "full"

    basets = utc(2000, 1, 1) if fullreprocess else (utc() - timedelta(days=8))
    LOG.info("Running full reprocess: %s basets: %s", fullreprocess, basets)
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            "select iemid, station, valid, rh_avg_qc from "
            "sm_daily d JOIN stations t on (d.station = t.id) "
            "where rh_avg_qc > 0 and valid > %s and t.network = 'ISUSM'",
            conn,
            params=(basets,),
            index_col=None,
        )
    LOG.info("Found %s obs", len(obs.index))
    with get_dbconn("iem") as pgconn:
        process(pgconn, obs)
        pgconn.commit()


if __name__ == "__main__":
    main(sys.argv)
