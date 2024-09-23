"""Compute the daily USCRN precipitation total.

Called from `RUN_20_AFTER.sh` for current date.
Called from `RUN_12Z.sh` for yesterday and a week ago.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import click
import pandas as pd
from metpy.units import units
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()
MM = units("mm")
INCH = units("inch")


def _do_update(icursor, valid, iemid, precip):
    """Inline."""
    icursor.execute(
        f"UPDATE summary_{valid.year} SET pday = %s "
        "WHERE day = %s and iemid = %s",
        (precip, valid.date(), iemid),
    )
    return icursor.rowcount


def run(valid: datetime):
    """Do Work."""
    nt = NetworkTable("USCRN")
    iem_pgconn = get_dbconn("iem")
    LOG.info("Processing %s", valid.date())
    with get_sqlalchemy_conn("uscrn") as conn:
        # Fetch enough data to cross all the dates
        df = pd.read_sql(
            "SELECT station, valid at time zone 'UTC' as utc_valid, precip_mm "
            "from alldata where valid > %s and valid < %s",
            conn,
            params=(
                valid - timedelta(days=1),
                valid + timedelta(days=2),
            ),
            index_col=None,
        )
    if df.empty:
        LOG.info("No data found for date: %s", valid.date())
        return
    df["utc_valid"] = df["utc_valid"].dt.tz_localize(timezone.utc)
    for station in nt.sts:
        iemid = nt.sts[station]["iemid"]
        tz = ZoneInfo(nt.sts[station]["tzname"])
        sts = datetime(valid.year, valid.month, valid.day, tzinfo=tz)
        ets = sts + timedelta(days=1)
        df2 = df[
            (df["station"] == station)
            & (df["utc_valid"] > sts)
            & (df["utc_valid"] <= ets)
        ]
        if df2.empty:
            continue
        precip = (df2["precip_mm"].sum() * MM).to(INCH).m
        LOG.info("station: %s precip: %.2f", station, precip)
        icursor = iem_pgconn.cursor()

        if _do_update(icursor, valid, iemid, precip) == 0:
            LOG.info("Adding summary table entry for %s %s", iemid, valid)
            icursor.execute(
                f"INSERT into summary_{valid.year}(iemid, day) "
                "VALUES (%s, %s)",
                (iemid, valid.date()),
            )
            _do_update(icursor, valid, iemid, precip)
        icursor.close()
        iem_pgconn.commit()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), required=True)
def main(dt: datetime):
    """Go Main Go."""
    run(dt)


if __name__ == "__main__":
    main()
