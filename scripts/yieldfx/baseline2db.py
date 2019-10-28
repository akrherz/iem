"""Copy the provided baseline data to the database"""
from __future__ import print_function
import glob
import os
import datetime

from pyiem.datatypes import speed
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("coop")
    cursor = pgconn.cursor()

    # Need to have a merge of windspeed and average rh
    dsm = {}
    ipgconn = get_dbconn("iem")
    icursor = ipgconn.cursor()
    icursor.execute(
        """
        select day, avg_sknt, avg_rh from summary where iemid = 37004
        and day >= '1980-01-01' ORDER by day ASC"""
    )
    for row in icursor:
        if row[1] is None or row[2] is None:
            dsm[row[0]] = dsm[row[0] - datetime.timedelta(days=1)]
        else:
            dsm[row[0]] = {
                "wind_speed": speed(row[1], "KTS").value("MPS"),
                "avg_rh": row[2],
            }

    os.chdir("baseline")
    for fn in glob.glob("*.met"):
        location = fn[:-4]
        cursor.execute(
            """
            DELETE from yieldfx_baseline where station = %s
        """,
            (location,),
        )
        print("Removed %s rows for station: %s" % (cursor.rowcount, location))
        for line in open(fn):
            line = line.strip()
            if not line.startswith("19") and not line.startswith("20"):
                continue
            tokens = line.split()
            valid = datetime.date(int(tokens[0]), 1, 1) + datetime.timedelta(
                days=int(tokens[1]) - 1
            )
            cursor.execute(
                """
            INSERT into yieldfx_baseline (station, valid,
            radn, maxt, mint, rain, windspeed, rh)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    location,
                    valid,
                    float(tokens[2]),
                    float(tokens[3]),
                    float(tokens[4]),
                    float(tokens[5]),
                    dsm[valid]["wind_speed"],
                    dsm[valid]["avg_rh"],
                ),
            )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
