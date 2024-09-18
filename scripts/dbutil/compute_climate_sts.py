"""Determine when a CLIMATE track site started...

Called from RUN_CLIMODAT_STATE.sh
"""

from datetime import date, timedelta

import click
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import logger

LOG = logger()


@click.command()
@click.option("--network", required=True)
def main(network: str):
    """Go Main Go"""
    asos = get_dbconn("coop")
    acursor = asos.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    floor = date.today() - timedelta(days=7)

    nt = NetworkTable(network, only_online=False)

    acursor.execute(
        f"SELECT station, min(day), max(day) from alldata_{network[:2]} "
        "GROUP by station ORDER by min ASC"
    )
    for row in acursor:
        station = row[0]
        if station not in nt.sts:
            LOG.info("%s is unknown in mesosite table", station)
            continue
        sts = row[1]
        ets = row[2]
        if ets >= floor:
            ets = None
        osts = nt.sts[station]["archive_begin"]
        oets = nt.sts[station]["archive_end"]
        oonline = nt.sts[station]["online"]
        online = ets is None
        noop = osts == sts and oets == ets and oonline == online
        loglvl = LOG.info if noop else LOG.warning
        loglvl(
            "%s%s [%s] sts:%s->%s ets:%s->%s OL:%s->%s",
            "  --> " if not noop else "",
            station,
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
        mcursor.execute(
            """
            UPDATE stations SET archive_begin = %s, archive_end = %s,
            online = %s WHERE iemid = %s
            """,
            (sts, ets, ets is None, nt.sts[station]["iemid"]),
        )
    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
