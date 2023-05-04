"""Compute the archive start time of a HADS/DCP/COOP network"""
import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
THISYEAR = datetime.datetime.now().year
HADSDB = get_dbconn("hads")
MESOSITEDB = get_dbconn("mesosite")


def get_minvalid(sid):
    """ "Do sid"""
    cursor = HADSDB.cursor()
    for yr in range(2002, THISYEAR + 1):
        cursor.execute(
            f"SELECT min(date(valid)) from raw{yr} WHERE station = %s", (sid,)
        )
        minv = cursor.fetchone()[0]
        if minv is not None:
            return minv
    return None


def do_network(network):
    """Do network"""
    nt = NetworkTable(network)
    for sid in nt.sts:
        sts = get_minvalid(sid)
        if sts is None:
            continue
        if (
            nt.sts[sid]["archive_begin"] is not None
            and nt.sts[sid]["archive_begin"] == sts
        ):
            continue
        osts = nt.sts[sid]["archive_begin"]
        fmt = "%Y-%m-%d %H:%M"
        LOG.warning(
            "%s [%s] new sts: %s OLD sts: %s",
            sid,
            network,
            sts.strftime(fmt),
            osts.strftime(fmt) if osts is not None else "null",
        )
        cursor = MESOSITEDB.cursor()
        cursor.execute(
            "UPDATE stations SET archive_begin = %s WHERE id = %s and "
            "network = %s",
            (sts, sid, network),
        )
        cursor.close()
        MESOSITEDB.commit()


def main(argv):
    """Go main Go"""
    if len(argv) == 1:
        # If we run without args, we pick a "random" network!
        cursor = MESOSITEDB.cursor()
        cursor.execute(
            "SELECT id from networks where id ~* 'DCP' or id ~* 'COOP' "
            "ORDER by id ASC"
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
