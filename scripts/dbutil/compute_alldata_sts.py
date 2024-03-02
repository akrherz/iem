"""Generalized mesosite archive_{begin,end} computation

For unknown reasons, direct calculation over alldata was yielding a horrible
query plan.  So we iterate over t<year> tables.

called from daily_drive_network.py for {asos,rwis}
"""

import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconnc, logger

LOG = logger()
ALLDATA = {}
START_YEAR = {
    "rwis": 1994,
    "asos": 1928,
    "other": 2003,
    "scan": 1987,
    "uscrn": 2001,
}
TODAY = datetime.date.today()


def get_minvalid(cursor, station, start_year):
    """ "Do sid"""
    for yr in range(start_year, TODAY.year + 1):
        cursor.execute(
            f"SELECT min(date(valid)) from t{yr} WHERE station = %s",
            (station,),
        )
        minv = cursor.fetchone()["min"]
        if minv is not None:
            return minv
    return None


def get_maxvalid(cursor, station, start_year):
    """ "Do sid"""
    for yr in range(TODAY.year, start_year - 1, -1):
        cursor.execute(
            f"SELECT max(date(valid)) from t{yr} WHERE station = %s",
            (station,),
        )
        val = cursor.fetchone()["max"]
        if val is not None:
            return val
    return None


def main(argv):
    """Go Main"""
    basets = datetime.date.today() - datetime.timedelta(days=365)
    (dbname, network) = argv[1:]

    pgconn, rcursor = get_dbconnc(dbname)
    mesosite, mcursor = get_dbconnc("mesosite")

    nt = NetworkTable(network, only_online=False)
    ids = list(nt.sts.keys())
    ids.sort()

    for station in ids:
        sts = get_minvalid(rcursor, station, START_YEAR[dbname])
        if sts is None:
            LOG.info("No alldata found for %s", station)
            continue
        ets = get_maxvalid(rcursor, station, START_YEAR[dbname])
        online = ets > basets
        if online:
            ets = None
        osts = nt.sts[station]["archive_begin"]
        oets = nt.sts[station]["archive_end"]
        oonline = nt.sts[station]["online"]
        noop = (sts == osts) and (ets == oets) and (online == oonline)
        loglevel = LOG.info if noop else LOG.warning
        loglevel(
            "%s%s %s->%s %s->%s OL:%s->%s",
            "" if noop else "----> ",
            station,
            osts,
            sts,
            oets,
            ets,
            oonline,
            online,
        )
        if noop:
            continue
        mcursor.execute(
            "UPDATE stations SET archive_begin = %s, archive_end = %s, "
            "online = %s WHERE iemid = %s",
            (sts, ets, online, nt.sts[station]["iemid"]),
        )
        mcursor.close()
        mesosite.commit()
        mcursor = mesosite.cursor()
    pgconn.close()
    mesosite.close()


if __name__ == "__main__":
    main(sys.argv)
