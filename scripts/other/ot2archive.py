"""
Dump iem database of OT data to archive
Runs at midnight and 12 UTC for previous day
"""
import datetime
import sys

# third party
from pyiem.util import get_dbconnc, logger, utc

LOG = logger()


def dowork(ts, ts2):
    """Process between these two timestamps please"""
    # Delete any obs from yesterday
    OTHER, ocursor = get_dbconnc("other")
    IEM, icursor = get_dbconnc("iem")
    ocursor.execute(
        "DELETE from alldata WHERE valid >= %s and valid < %s", (ts, ts2)
    )

    # Get obs from Access
    icursor.execute(
        "SELECT c.*, t.id from current_log c JOIN stations t on "
        "(t.iemid = c.iemid) WHERE valid >= %s and valid < %s "
        "and t.network in ('OT', 'WMO_BUFR_SRF')",
        (ts, ts2),
    )
    if icursor.rowcount == 0:
        LOG.warning("found no results for ts: %s ts2: %s", ts, ts2)

    for row in icursor:
        pday = 0
        if row["pday"] is not None and float(row["pday"]) > 0:
            pday = row["pday"]
        alti = row["alti"]
        if alti is None and row["mslp"] is not None:
            alti = row["mslp"] * 0.03
        args = (
            row["id"],
            row["valid"],
            row["tmpf"],
            row["dwpf"],
            row["drct"],
            row["sknt"],
            alti,
            pday,
            row["gust"],
            row["srad"],
            row["relh"],
        )
        ocursor.execute(
            "INSERT into alldata(station, valid, tmpf, dwpf, drct, sknt, "
            "alti, pday, gust, srad, relh) values "
            "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            args,
        )

    ocursor.close()
    OTHER.commit()


def main(argv):
    """Run for a given 6z to 6z period."""
    ts = utc(int(argv[1]), int(argv[2]), int(argv[3]), 6)
    ts2 = ts + datetime.timedelta(hours=24)
    dowork(ts, ts2)


if __name__ == "__main__":
    main(sys.argv)
