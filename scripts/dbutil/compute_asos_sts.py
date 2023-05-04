"""Update metadata database with archive start for METAR sites.

Looks at the asos database and finds the first observation from a site.
"""
import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def main(network):
    """GO!"""
    basets = datetime.date.today()

    asos = get_dbconn("asos")
    acursor = asos.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()

    table = NetworkTable(network, only_online=False)
    ids = list(table.sts.keys())

    acursor.execute(
        "SELECT station, min(date(valid)), max(date(valid)) from alldata "
        "WHERE station in %s GROUP by station ORDER by min ASC",
        (tuple(ids),),
    )
    for row in acursor:
        station = row[0]
        if table.sts[station]["archive_begin"] != row[1]:
            LOG.warning(
                "Updated %s STS WAS: %s NOW: %s",
                station,
                table.sts[station]["archive_begin"],
                row[1],
            )

            mcursor.execute(
                "UPDATE stations SET archive_begin = %s WHERE id = %s "
                "and network = %s",
                (row[1], station, network),
            )
            if mcursor.rowcount == 0:
                LOG.warning("ERROR: No rows updated for %s", station)

        # Site without data in past year is offline!
        if (basets - row[2]).days > 365:
            if table.sts[station]["archive_end"] != row[2]:
                LOG.warning(
                    "Updated %s ETS WAS: %s NOW: %s",
                    station,
                    table.sts[station]["archive_end"],
                    row[2],
                )

                mcursor.execute(
                    "UPDATE stations SET archive_end = %s, online = 'f' "
                    "WHERE id = %s and network = %s",
                    (row[2], station, network),
                )

        # If it was offline and now is on, correct this
        if (basets - row[2]).days < 365 and table.sts[station][
            "archive_end"
        ] is not None:
            LOG.warning(
                "Updated %s ETS WAS: %s NOW: None" "",
                station,
                table.sts[station]["archive_end"],
            )

            mcursor.execute(
                "UPDATE stations SET archive_end = null, online = 't' "
                "WHERE id = %s and network = %s",
                (station, network),
            )

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main(sys.argv[1])
