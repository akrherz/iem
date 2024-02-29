"""Compute archive_start / archive_end logic for COOP network sites.

called from RUN_CLIMODAT_STATE.sh
"""

import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconnc, logger

LOG = logger()
TODAY = datetime.date.today()


def do_network(network):
    """Do network"""
    nt = NetworkTable(network, only_online=False)
    iem, icursor = get_dbconnc("iem")
    for sid in nt.sts:
        icursor.execute(
            "select min(day), max(day) from summary WHERE "
            "iemid = %s and (max_tmpf is not null or min_tmpf is not null "
            "or pday is not null)",
            (nt.sts[sid]["iemid"],),
        )
        row = icursor.fetchone()
        sts = row["min"]
        ets = row["max"]
        if sts is None:
            LOG.warning("sid: %s has no iemaccess data?", sid)
            continue
        if ets.year >= (TODAY.year - 1):
            ets = None
        osts = nt.sts[sid]["archive_begin"]
        oets = nt.sts[sid]["archive_end"]
        oonline = nt.sts[sid]["online"]
        online = ets is None
        noop = osts == sts and oets == ets and oonline == online
        loglvl = LOG.info if noop else LOG.warning
        loglvl(
            "%s%s [%s] sts:%s->%s ets:%s->%s OL:%s->%s",
            "  --> " if not noop else "",
            sid,
            network,
            osts,
            sts,
            oets,
            ets,
            oonline,
            online,
        )
        if noop:
            continue
        mconn, mcursor = get_dbconnc("mesosite")
        mcursor.execute(
            """
            UPDATE stations SET archive_begin = %s, archive_end = %s,
            online = %s WHERE iemid = %s
            """,
            (sts, ets, ets is None, nt.sts[sid]["iemid"]),
        )
        mcursor.close()
        mconn.commit()
    iem.close()


def main(argv):
    """Go main Go"""
    network = argv[1]
    do_network(network)


if __name__ == "__main__":
    main(sys.argv)
