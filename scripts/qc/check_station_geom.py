"""
  Check to make sure the station metadata is reasonable!
called from RUN_MIDNIGHT.sh
"""
from __future__ import print_function
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    pgconn = get_dbconn("mesosite", user="nobody")
    mcursor = pgconn.cursor()

    mcursor.execute(
        """
     SELECT id, network, ST_x(geom), ST_y(geom), modified from stations WHERE
     ST_x(geom) >= 180 or ST_x(geom) <= -180
     or ST_y(geom) > 90 or ST_y(geom) < -90
    """
    )
    for row in mcursor:
        print("check_station_geom.py LOC QC FAIL")
        print(row)


if __name__ == "__main__":
    main()
