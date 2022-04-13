"""Generalized mesosite archive_begin computation

For backends that implement alldata(station, valid)"""
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
ALLDATA = {"USCRN": "uscrn_alldata"}


def main(argv):
    """Go Main"""
    (dbname, network) = argv[1:]

    pgconn = get_dbconn(dbname)
    rcursor = pgconn.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()

    table = NetworkTable(network)

    rcursor.execute(
        "SELECT station, min(date(valid)), max(date(valid)) from "
        f"{ALLDATA.get(network, 'alldata')} "
        "GROUP by station ORDER by min ASC"
    )
    for row in rcursor:
        station = row[0]
        if station not in table.sts:
            continue
        if table.sts[station]["archive_begin"] != row[1]:
            LOG.warning(
                "Updated %s STS WAS: %s NOW: %s",
                station,
                table.sts[station]["archive_begin"],
                row[1],
            )

        mcursor.execute(
            "UPDATE stations SET archive_begin = %s "
            "WHERE id = %s and network = %s",
            (row[1], station, network),
        )
        if mcursor.rowcount == 0:
            LOG.warning("ERROR: No rows updated for %s", station)

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main(sys.argv)
