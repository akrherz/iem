"""Compute archive_start / archive_end logic for COOP network sites.

called from RUN_CLIMODAT_STATE.sh
"""

from datetime import date

import click
from psycopg import Connection
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger
from sqlalchemy import text

LOG = logger()
TODAY = date.today()


def do_network(conn: Connection, network: str):
    """Do network"""
    nt = NetworkTable(network, only_online=False)
    for sid in nt.sts:
        res = conn.execute(
            text("""
        select min(day), max(day) from summary WHERE iemid = :iemid and
        (max_tmpf is not null or min_tmpf is not null or pday is not null)
            """),
            {"iemid": nt.sts[sid]["iemid"]},
        )
        row = res.fetchone()
        sts = row[0]
        ets = row[1]
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
        mconn.close()


@click.command()
@click.option("--network", required=True)
def main(network: str):
    """Go main Go"""
    with get_sqlalchemy_conn("iem") as conn:
        do_network(conn, network)


if __name__ == "__main__":
    main()
