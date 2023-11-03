"""Compute the archive start time of a HADS/DCP network.

called from windrose/daily_drive_network.py
"""
import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
TODAY = datetime.date.today()
HADSDB = get_dbconn("hads")
MESOSITEDB = get_dbconn("mesosite")


def get_minvalid(sid):
    """ "Do sid"""
    cursor = HADSDB.cursor()
    for yr in range(2002, TODAY.year + 1):
        cursor.execute(
            f"SELECT min(date(valid)) from raw{yr} WHERE station = %s", (sid,)
        )
        minv = cursor.fetchone()[0]
        if minv is not None:
            return minv
    return None


def get_maxvalid(sid):
    """ "Do sid"""
    cursor = HADSDB.cursor()
    for yr in range(TODAY.year, 2001, -1):
        cursor.execute(
            f"SELECT max(date(valid)) from raw{yr} WHERE station = %s", (sid,)
        )
        val = cursor.fetchone()[0]
        if val is not None:
            return val
    return None


def do_network(network):
    """Do network"""
    nt = NetworkTable(network)
    for sid in nt.sts:
        sts = get_minvalid(sid)
        osts = nt.sts[sid]["archive_begin"]
        ets = get_maxvalid(sid)
        if ets is not None and ets.year >= (TODAY.year - 1):
            ets = None
        oets = nt.sts[sid]["archive_end"]
        LOG.info(
            "%s [%s] sts:%s|%s ets:%s|%s",
            sid,
            network,
            osts,
            sts,
            oets,
            ets,
        )
        if osts == sts and oets == ets:
            continue
        LOG.warning(
            "%s [%s] sts:%s->%s ets:%s->%s",
            sid,
            network,
            osts,
            sts,
            oets,
            ets,
        )
        cursor = MESOSITEDB.cursor()
        cursor.execute(
            """
            UPDATE stations SET archive_begin = %s, archive_end = %s,
            online = %s WHERE iemid = %s
            """,
            (sts, ets, ets is None, nt.sts[sid]["iemid"]),
        )
        cursor.close()
        MESOSITEDB.commit()


def main(argv):
    """Go main Go"""
    if len(argv) == 1:
        # If we run without args, we pick a "random" DCP network!
        # COOP networks can't reliably use this script's logic
        cursor = MESOSITEDB.cursor()
        cursor.execute(
            "SELECT id from networks where id ~* 'DCP' ORDER by id ASC"
        )
        networks = []
        for row in cursor:
            networks.append(row[0])
        jday = int(datetime.date.today().strftime("%j"))
        network = networks[jday % len(networks)]
        LOG.info("auto-picked %s", network)
    else:
        network = argv[1]
    do_network(network)


if __name__ == "__main__":
    main(sys.argv)
