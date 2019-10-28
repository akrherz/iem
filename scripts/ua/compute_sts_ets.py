"""Update mesosite with sts and ets"""
from __future__ import print_function
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    MESOSITE = get_dbconn("mesosite")
    mcursor = MESOSITE.cursor()
    POSTGIS = get_dbconn("postgis", user="nobody")
    pcursor = POSTGIS.cursor()

    pcursor.execute(
        """
        SELECT station, min(valid), max(valid), count(*) from
        raob_flights GROUP by station ORDER by count DESC
    """
    )
    for row in pcursor:
        station = row[0]
        sts = row[1]
        ets = row[2]
        online = False
        if ets.year == 2013:
            ets = None
            online = True
        mcursor.execute(
            """
            UPDATE stations SET online = %s, archive_begin = %s,
            archive_end = %s WHERE network = 'RAOB' and id = %s
        """,
            (online, sts, ets, station),
        )
        if mcursor.rowcount != 1:
            print("%s %s %s %s" % (station, sts, ets, row[3]))

    mcursor.close()
    MESOSITE.commit()
    MESOSITE.close()


if __name__ == "__main__":
    main()
