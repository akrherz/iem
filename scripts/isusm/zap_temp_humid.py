"""Properly zap a period of data from the database"""

import subprocess
from datetime import datetime

import click
from pyiem.database import get_dbconn
from pyiem.util import logger

LOG = logger()


def do_isuag(nwsli, sts, ets):
    """Do ISUAG Table"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    # Cull minute
    cursor.execute(
        """
        UPDATE sm_minute SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        rh_qc = null, rh_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts, ets),
    )
    LOG.info("    sm_15minute updated %s rows", cursor.rowcount)
    # Cull hourly
    cursor.execute(
        """
        UPDATE sm_hourly SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        rh_qc = null, rh_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts, ets),
    )
    LOG.info("    sm_hourly updated %s rows", cursor.rowcount)
    # cull daily
    cursor.execute(
        """
        UPDATE sm_daily SET
        tair_c_avg_qc = null, tair_c_avg_f = 'M',
        tair_c_min_qc = null, tair_c_min_f = 'M',
        tair_c_max_qc = null, tair_c_max_f = 'M',
        rh_avg_qc = null, rh_avg_f = 'M'
        WHERE station = %s and valid >= %s and valid <= %s
    """,
        (nwsli, sts.date(), ets.date()),
    )
    LOG.info("    sm_daily updated %s rows", cursor.rowcount)
    cursor.close()
    pgconn.commit()
    pgconn.close()


def do_iem(nwsli, sts, ets):
    """Update the summary table"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    # cull iemre daily
    cursor.execute(
        """
        UPDATE summary s SET
        max_tmpf = null, min_tmpf = null, max_dwpf = null, min_dwpf = null,
        avg_rh = null, min_rh = null, max_rh = null
        FROM stations t
        WHERE t.id = %s and t.network = 'ISUSM' and s.iemid = t.iemid
        and day >= %s and day <= %s
    """,
        (nwsli, sts.date(), ets.date()),
    )
    LOG.info("    summary updated %s rows", cursor.rowcount)
    cursor.close()
    pgconn.commit()
    pgconn.close()


@click.command()
@click.option("--station", help="Station Identifier", required=True)
@click.option(
    "--sts", help="Start Timestamp", required=True, type=click.DateTime()
)
@click.option(
    "--ets", help="End Timestamp", required=True, type=click.DateTime()
)
def main(station: str, sts: datetime, ets: datetime):
    """Go Main Go"""
    res = input(f"{station} {sts}->{ets}, OK? y/[n] ")
    if str(res) != "y":
        print("ABORT")
        return
    do_iem(station, sts, ets)
    do_isuag(station, sts, ets)
    print("Redoing estimates")
    subprocess.call(["python", "fix_temps.py"])


if __name__ == "__main__":
    main()
