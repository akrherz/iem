"""Initially import the smos points into the database
     202104
  202103  202617
     202616

155930 is the min

513 rows in the y

offset 75 as per experimentation
x grid wrapping experimentation too, sigh

This file was provided by Jason Patton
"""
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("smos")
    scursor = pgconn.cursor()

    for line in open("/tmp/smos_grid.txt").readlines()[1:]:
        (sid, lon, lat) = line.split(",")
        sid = int(sid)
        gridy = (sid - 75) % 513
        gridx = (sid - 75) / 513
        if gridx > 9000:
            gridx = gridx - 9236
        scursor.execute(
            "INSERT into grid(idx,gridx,gridy,geom) VALUES (%s, %s, %s, "
            "'SRID=4326;POINT(%s %s)'",
            (sid, gridx, gridy, lon, lat),
        )

    pgconn.commit()


if __name__ == "__main__":
    main()
