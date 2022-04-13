"""Figure out when the ISUSM data started..."""

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Go Main"""
    isuag = get_dbconn("isuag")
    icursor = isuag.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()

    table = NetworkTable("ISUSM", only_online=False)

    icursor.execute(
        "SELECT station, min(date(valid)), max(date(valid)) from sm_hourly "
        "GROUP by station ORDER by min ASC"
    )
    for row in icursor:
        station = row[0]
        if station not in table.sts:
            LOG.warning(
                "Whoa station: %s does not exist in metadatabase?",
                station,
            )
            continue
        if table.sts[station]["archive_begin"] != row[1]:
            LOG.warning(
                "Updated %s STS WAS: %s NOW: %s" "",
                station,
                table.sts[station]["archive_begin"],
                row[1],
            )

        mcursor.execute(
            "UPDATE stations SET archive_begin = %s "
            "WHERE id = %s and network = %s",
            (row[1], station, "ISUSM"),
        )
        if mcursor.rowcount == 0:
            LOG.warning("ERROR: No rows updated for %s", station)

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
