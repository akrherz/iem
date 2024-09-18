"""Compute the archive start time of a HADS/DCP network.

called from windrose/daily_drive_network.py
"""

from datetime import date
from typing import Optional

import click
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()
TODAY = date.today()
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


def do_network(network: str):
    """Do network"""
    nt = NetworkTable(network, only_online=False)
    for sid in nt.sts:
        osts = nt.sts[sid]["archive_begin"]
        oets = nt.sts[sid]["archive_end"]
        sts = get_minvalid(sid)
        ets = get_maxvalid(sid)
        if ets is not None and ets.year >= (TODAY.year - 1):
            ets = None
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


@click.command()
@click.option("--network", required=False)
def main(network: Optional[str]):
    """Go main Go"""
    if network is None:
        # If we run without args, we pick a "random" DCP network!
        # COOP networks can't reliably use this script's logic
        cursor = MESOSITEDB.cursor()
        cursor.execute(
            "SELECT id from networks where id ~* 'DCP' ORDER by id ASC"
        )
        networks = [row[0] for row in cursor]
        jday = int(date.today().strftime("%j"))
        network = networks[jday % len(networks)]
        LOG.info("auto-picked %s", network)
    do_network(network)


if __name__ == "__main__":
    main()
