"""Backfill IEMAccess Summary table.

Some of the variables don't get properly updated in the summary table.

cronjob from RUN_2AM.sh
"""

from datetime import datetime

import click
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.util import convert_value, logger

LOG = logger()


def process(pgconn, obs: pd.DataFrame):
    """option 1"""
    wcursor = pgconn.cursor()
    for iemid, row in obs.iterrows():
        table = f"summary_{row['valid']:%Y}"
        wcursor.execute(
            f"""
    UPDATE {table} SET avg_rh = %s, max_gust = %s, max_gust_ts = %s,
    avg_sknt = %s WHERE iemid = %s and day = %s
            """,
            (
                row["rh_avg_qc"],
                convert_value(row["ws_mph_max_qc"], "mph", "knot"),
                row["ws_mph_tmx_qc"],
                convert_value(row["ws_mph_qc"], "mph", "knot"),
                iemid,
                row["valid"],
            ),
        )
        if wcursor.rowcount == 0:
            LOG.warning("Adding summary row for iemid: %s", iemid)
            wcursor.execute(
                f"""
    INSERT INTO {table} (iemid, day, avg_rh, max_gust, max_gust_ts, avg_sknt)
    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    iemid,
                    row["valid"],
                    row["rh_avg_qc"],
                    convert_value(row["ws_mph_max_qc"], "mph", "knot"),
                    row["ws_mph_tmx_qc"],
                    convert_value(row["ws_mph_qc"], "mph", "knot"),
                ),
            )
    wcursor.close()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to process")
def main(dt: datetime):
    """Go Main Go"""
    dt = dt.date()
    with get_sqlalchemy_conn("isuag") as conn:
        obs = pd.read_sql(
            sql_helper("""
    select iemid, station, valid, rh_avg_qc, ws_mph_tmx_qc, ws_mph_qc,
    ws_mph_max_qc
    from sm_daily d JOIN stations t on (d.station = t.id)
    where valid = :dt and t.network = 'ISUSM'
    """),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    with get_sqlalchemy_conn("iem") as conn:
        summary = pd.read_sql(
            sql_helper("""
    select d.iemid, avg_rh, max_gust, max_gust_ts, avg_sknt
    from summary d JOIN stations t on (d.iemid = t.iemid)
    where day = :dt and t.network = 'ISUSM'
    """),
            conn,
            params={"dt": dt},
            index_col="iemid",
        )
    obs = obs.join(summary, how="left", rsuffix="_summary")
    LOG.info(
        "Found %s obs for date: %s",
        len(obs.index),
        dt,
    )
    with get_dbconn("iem") as pgconn:
        process(pgconn, obs)
        pgconn.commit()


if __name__ == "__main__":
    main()
