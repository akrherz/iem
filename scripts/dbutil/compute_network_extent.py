"""Compute the spatial extent of a network"""
from __future__ import print_function

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()

    # Buffer point a bit so that 1 station networks are not points
    cursor.execute(
        """WITH extents as (
        SELECT network,
        ST_SetSRID(ST_Extent(ST_Buffer(geom, 0.1))::geometry, 4326) as ste
        from stations GROUP by network)

        UPDATE networks SET extent = e.ste FROM extents e
        WHERE e.network = networks.id and
        (extent is null or not ST_Equals(e.ste, extent))
        RETURNING id, st_xmin(extent), st_ymin(extent), st_xmax(extent),
        st_ymax(extent)"""
    )

    if cursor.rowcount > 0:
        print("compute_network_extent updated %s rows" % (cursor.rowcount,))
    if cursor.rowcount < 50:
        for row in cursor:
            print(
                "   %s -> %.4f %.4f %.4f %.4f"
                % (row[0], row[1], row[2], row[3], row[4])
            )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
