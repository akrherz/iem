"""Determine when a CLIMATE track site started..."""
from __future__ import print_function
import sys

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc


def main():
    """Go Main Go"""
    asos = get_dbconn("coop")
    acursor = asos.cursor()
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()

    net = sys.argv[1]

    nt = NetworkTable(net)

    acursor.execute(
        """SELECT station, min(day) from alldata_%s GROUP by station
      ORDER by min ASC"""
        % (net[:2])
    )
    for row in acursor:
        station = row[0]
        # Use 12 UTC as the timestamp so to avoid timezone issues with very old
        # dates, for example 00 UTC on 1 Jan 1893 would go to 31 Dec 1892
        ts = utc(row[1].year, row[1].month, row[1].day, 12, 0)
        if station not in nt.sts:
            continue
        if nt.sts[station]["archive_begin"] != ts:
            print(
                ("Updated %s STS WAS: %s NOW: %s" "")
                % (station, nt.sts[station]["archive_begin"], ts)
            )

            mcursor.execute(
                """UPDATE stations SET archive_begin = %s
                 WHERE id = %s and network = %s""",
                (ts, station, net),
            )

    mcursor.close()
    mesosite.commit()
    mesosite.close()


if __name__ == "__main__":
    main()
