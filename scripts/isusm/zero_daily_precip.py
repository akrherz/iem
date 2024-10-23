"""Sometimes we need to completely zero out precip for a day

Likely due to water being dumped into the tipping bucket to clean it :/
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import click
from pyiem.database import get_dbconn


def zero_hourly(station, sts, ets):
    """Zero out the hourly data"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    for table in ["sm_hourly", "sm_minute"]:
        cursor.execute(
            f"""
            UPDATE {table}
            SET rain_in_tot_qc = 0, rain_in_tot_f = 'Z', rain_in_tot = 0
            WHERE station = %s and valid > %s and valid <= %s
        """,
            (station, sts, ets),
        )
        print("%s updated %s rows" % (table, cursor.rowcount))
    cursor.close()
    pgconn.commit()


def zero_daily(station, date):
    """Zero out the daily data"""
    pgconn = get_dbconn("isuag")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        UPDATE sm_daily
        SET rain_in_tot_qc = 0, rain_in_tot_f = 'Z', rain_in_tot = 0
        WHERE station = %s and valid = %s
    """,
        (station, date),
    )
    print("sm_daily updated %s rows" % (cursor.rowcount,))
    cursor.close()
    pgconn.commit()


def zero_iem(station, date):
    """Zero out the hourly data"""
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        UPDATE summary s
        SET pday = 0
        FROM stations t
        WHERE s.iemid = t.iemid and t.id = %s and t.network = 'ISUSM'
        and day = %s
    """,
        (station, date),
    )
    print("summary updated %s rows" % (cursor.rowcount,))
    cursor.close()
    pgconn.commit()


@click.command()
@click.option("--station", required=True, help="ISUSM Station ID")
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    required=True,
    help="Date to zero out",
)
def main(station: str, dt: datetime):
    """Go Main"""
    dt = dt.date()
    # Our weather stations are in CST, so the 'daily' precip is for a 6z to 6z
    # period and not calendar day, the hourly values are in the rears
    sts = datetime(dt.year, dt.month, dt.day, 6)
    sts = sts.replace(tzinfo=ZoneInfo("UTC"))
    ets = sts + timedelta(hours=24)
    zero_hourly(station, sts, ets)
    zero_daily(station, dt)
    zero_iem(station, dt)


if __name__ == "__main__":
    main()
