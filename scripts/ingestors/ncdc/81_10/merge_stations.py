"""
  Create IEM station entries

  network: NCDC81
"""
from __future__ import print_function

from pyiem.util import get_dbconn


def compute_stations(cursor):
    """ Logic to resolve, which stations we care about and add necessary
    station metadata about them! """

    pass1 = []
    for line in open("temp-inventory.txt"):
        pass1.append(line[:11])

    # Now we iterate over the precip inventory
    for line in open("prcp-inventory.txt"):
        if line[:11] not in pass1:
            continue
        # We have a station we care about!
        sid = line[:11]
        lat = float(line[12:20])
        lon = float(line[21:30])
        elev = float(line[31:37])
        state = line[38:40]
        name = line[41:71].strip()

        cursor.execute(
            """
        INSERT into stations
        (id, network, geom, elevation, name, country,
        state, online, plot_name, archive_begin, archive_end, metasite)
        VALUES
        (%s, 'NCDC81', 'SRID=4326;POINT(%s %s)', %s, %s, %s,
        %s, 't', %s, '1981-01-01', '2010-12-31', 't')
        """,
            (sid, lon, lat, elev, name, sid[:2], state, name),
        )


def main():
    """ Go main Go """
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    compute_stations(cursor)
    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    # Go
    main()
