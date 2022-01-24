"""Compute the daily USCRN precipitation total.

Called from `RUN_20_AFTER.sh` for current date.
Called from `RUN_12Z.sh` for yesterday and a week ago.
"""
# pylint: disable=cell-var-from-loop
import sys
import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from pyiem.util import logger, get_dbconn, get_dbconnstr
from pyiem.network import Table as NetworkTable
from metpy.units import units
from pandas import read_sql

LOG = logger()
MM = units("mm")
INCH = units("inch")


def run(valid):
    """Do Work."""
    nt = NetworkTable("USCRN")
    iem_pgconn = get_dbconn("iem")
    LOG.debug("Processing %s", valid.date())
    # Fetch enough data to cross all the dates
    df = read_sql(
        "SELECT station, valid at time zone 'UTC' as utc_valid, precip_mm "
        "from uscrn_alldata where valid > %s and valid < %s",
        get_dbconnstr("other"),
        params=(
            valid - datetime.timedelta(days=1),
            valid + datetime.timedelta(days=2),
        ),
        index_col=None,
    )
    if df.empty:
        LOG.info("No data found for date: %s", valid.date())
        return
    df["utc_valid"] = df["utc_valid"].dt.tz_localize(datetime.timezone.utc)
    for station in nt.sts:
        iemid = nt.sts[station]["iemid"]
        tz = ZoneInfo(nt.sts[station]["tzname"])
        sts = datetime.datetime(valid.year, valid.month, valid.day, tzinfo=tz)
        ets = sts + datetime.timedelta(days=1)
        df2 = df[
            (df["station"] == station)
            & (df["utc_valid"] > sts)
            & (df["utc_valid"] <= ets)
        ]
        if df2.empty:
            continue
        precip = (df2["precip_mm"].sum() * MM).to(INCH).m
        LOG.debug("station: %s precip: %.2f", station, precip)
        icursor = iem_pgconn.cursor()

        def _do_update():
            """Inline."""
            icursor.execute(
                f"UPDATE summary_{valid.year} SET pday = %s "
                "WHERE day = %s and iemid = %s",
                (precip, valid.date(), iemid),
            )
            return icursor.rowcount

        if _do_update() == 0:
            LOG.debug("Adding summary table entry for %s %s", iemid, valid)
            icursor.execute(
                f"INSERT into summary_{valid.year}(iemid, day) "
                "VALUES (%s, %s)",
                (iemid, valid.date()),
            )
            _do_update()
        icursor.close()
        iem_pgconn.commit()


def main(argv):
    """Go Main Go."""
    if len(argv) == 4:
        valid = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        valid = datetime.datetime.now()
    run(valid)


if __name__ == "__main__":
    main(sys.argv)
