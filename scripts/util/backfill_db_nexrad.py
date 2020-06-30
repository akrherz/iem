"""Create WMS-T database entries as necessary."""
import datetime
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Go Main!"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    now = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]), 0, 0)
    ets = now + datetime.timedelta(days=1)

    product = sys.argv[4].lower()
    table = "nexrad_%s_tindex" % (product,)

    while now < ets:
        cursor.execute(f"SELECT * from {table} WHERE datetime = %s", (now,))

        if cursor.rowcount == 0:
            print("Insert %s" % (now,))
            fn = now.strftime(
                "/mesonet/ARCHIVE/data/%Y/%m/%d/"
                f"GIS/uscomp/{product}_%Y%m%d%H%M.png"
            )
            cursor.execute(
                f"""
            INSERT into {table} (datetime, filepath, the_geom) VALUES
            (%s, %s,
            'SRID=4326;
             MULTIPOLYGON(((-126 50,-66 50,-66 24,-126 24,-126 50)))')
            """,
                (now, fn),
            )

        now += datetime.timedelta(minutes=5)

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main(sys.argv)
