"""Generalized mesosite archive_begin computation

For backends that implement alldata(station, valid)"""
import datetime
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()
ALLDATA = {"USCRN": "uscrn_alldata"}


def main(argv):
    """Go Main"""
    basets = datetime.date.today()
    (dbname, network) = argv[1:]

    pgconn = get_dbconn(dbname)
    rcursor = pgconn.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()

    table = NetworkTable(network, only_online=False)
    ids = list(table.sts.keys())

    rcursor.execute(
        f"""
        SELECT station, min(date(valid)), max(date(valid)) from
        {ALLDATA.get(network, 'alldata')} WHERE station = ANY(%s)
        GROUP by station ORDER by min ASC
        """,
        (ids,),
    )
    for row in rcursor:
        station = row[0]
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
        # Site without data in past year is offline!
        if (basets - row[2]).days > 365 and table.sts[station][
            "archive_end"
        ] != row[2]:
            LOG.warning(
                "Updated %s ETS WAS: %s NOW: %s -> setting offline",
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
                "Updated %s ETS WAS: %s NOW: None -> setting online",
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
    main(sys.argv)
