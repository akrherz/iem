"""Create NCEI91 station entries."""

from pyiem.util import get_dbconn


def compute_stations(cursor):
    """Logic to resolve, which stations we care about and add necessary
    station metadata about them!"""

    with open("inventory_30yr.txt", encoding="ascii") as fh:
        for line in fh:
            # We have a station we care about!
            sid = line[:11]
            lat = float(line[12:20])
            lon = float(line[21:30])
            elev = float(line[31:37])
            state = line[38:40]
            name = line[41:71].strip()

            cursor.execute(
                "SELECT id from stations where id = %s and network = 'NCEI91'",
                (sid,),
            )
            if cursor.rowcount == 1:
                continue
            cursor.execute(
                """
                INSERT into stations (id, network, geom, elevation, name,
                country, state, online, plot_name, archive_begin, archive_end,
                metasite, ncei91)
                VALUES (%s, 'NCEI91', ST_POINT(%s, %s, 4326), %s,
                %s, %s, %s, 't', %s, '1991-01-01', '2020-12-31', 't', %s)
                """,
                (sid, lon, lat, elev, name, sid[:2], state, name, sid),
            )
            print(f"adding {sid}")


def main():
    """Go main Go"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    compute_stations(cursor)
    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    # Go
    main()
