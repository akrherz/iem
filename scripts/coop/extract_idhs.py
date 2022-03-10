"""Extraction as requested by IA Public Health"""
import sys

from pyiem.util import get_dbconn


def main(argv):
    """Do Something"""
    year = int(argv[1])
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    cursor2 = pgconn.cursor()
    pgconn2 = get_dbconn("coop")
    cursor3 = pgconn2.cursor()
    cursor.execute(
        "SELECT ugc, ST_X(centroid), ST_Y(centroid) "
        "from ugcs where state = 'IA' and substr(ugc,3,1) = 'C' "
        "and end_ts is null ORDER by ugc ASC"
    )
    for row in cursor:
        fips = row[0][3:]
        # Get closest climodat site
        cursor2.execute(
            "SELECT id, ST_Distance(geom, "
            "ST_SetSRID(ST_GeomFromText('POINT(%s %s)'), 4326)) "
            "from stations where network = 'IACLIMATE' and id != 'IA0000' "
            "and substr(id,3,1) != 'C' and online "
            "ORDER by st_distance ASC LIMIT 1",
            (row[1], row[2]),
        )
        sid = cursor2.fetchone()[0]

        cursor3.execute(
            "SELECT year, month, max(high), min(low), avg((high+low)/2.), "
            "sum(precip), sum(case when high >= 95 then 1 else 0 end), "
            "sum(case when low >= 70 then 1 else 0 end) from alldata_ia WHERE "
            "station = %s and year = %s GROUP by year, month",
            (sid, year),
        )
        for row2 in cursor3:
            print(
                ",".join(
                    [
                        str(i)
                        for i in [
                            fips,
                            row2[0],
                            row2[1],
                            row2[2],
                            row2[3],
                            row2[4],
                            row2[5],
                            row2[6],
                            row2[7],
                        ]
                    ]
                )
            )


if __name__ == "__main__":
    main(sys.argv)
