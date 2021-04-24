"""Determine when a CLIMATE track site started..."""
import sys
import datetime

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc, logger

LOG = logger()


def main(argv):
    """Go Main Go"""
    asos = get_dbconn("coop")
    acursor = asos.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    floor = datetime.date.today() - datetime.timedelta(days=7)

    net = argv[1]

    nt = NetworkTable(net, only_online=False)

    acursor.execute(
        f"SELECT station, min(day), max(day) from alldata_{net[:2]} "
        "GROUP by station ORDER by min ASC"
    )
    for row in acursor:
        station = row[0]
        # Use 12 UTC as the timestamp so to avoid timezone issues with very old
        # dates, for example 00 UTC on 1 Jan 1893 would go to 31 Dec 1892
        sts = utc(row[1].year, row[1].month, row[1].day, 12, 0)
        ets = utc(row[2].year, row[2].month, row[2].day, 12, 0)
        if station not in nt.sts:
            LOG.info("%s is unknown in mesosite table", station)
            continue
        meta = nt.sts[station]
        if (
            meta["archive_begin"] is None
            or meta["archive_begin"].date() != sts.date()
        ):
            LOG.info(
                "Updated %s STS WAS: %s NOW: %s" "",
                station,
                nt.sts[station]["archive_begin"],
                sts,
            )

            mcursor.execute(
                "UPDATE stations SET archive_begin = %s "
                "WHERE id = %s and network = %s",
                (sts, station, net),
            )
        archive_end = ets
        if ets.date() > floor:
            archive_end = None
        if (
            archive_end is None and meta["archive_end"] is not None
        ) or archive_end != meta["archive_end"]:
            LOG.info(
                "Updated %s ETS WAS: %s NOW: %s" "",
                station,
                nt.sts[station]["archive_end"],
                archive_end,
            )

            mcursor.execute(
                "UPDATE stations SET archive_end = %s "
                "WHERE id = %s and network = %s",
                (archive_end, station, net),
            )

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main(sys.argv)
