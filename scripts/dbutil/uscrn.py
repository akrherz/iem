"""Process the USCRN station table

ftp://ftp.ncdc.noaa.gov/pub/data/uscrn/products/stations.tsv
"""

import pandas as pd
from pyiem.util import get_dbconn


def main():
    """Go"""
    pgconn = get_dbconn("mesosite", user="mesonet")
    cursor = pgconn.cursor()
    df = pd.read_csv("stations.tsv", sep=r"\t", engine="python")
    df["stname"] = df["LOCATION"] + " " + df["VECTOR"]
    for _, row in df.iterrows():
        station = row["WBAN"]
        if station == "UN" or pd.isnull(station):
            continue
        cursor.execute(
            """
            SELECT * from stations where id = %s and network = 'USCRN'
        """,
            (station,),
        )
        if cursor.rowcount == 0:
            cursor.execute(
                """
            INSERT into stations (id, network) VALUES (%s, 'USCRN')
            """,
                (station,),
            )
        cursor.execute(
            """
        UPDATE stations
        SET geom = 'SRID=4326;POINT(%(LONGITUDE)s %(LATITUDE)s)',
        country = %(COUNTRY)s, state = %(STATE)s,
        name = %(stname)s, elevation = %(ELEVATION)s,
        online = 't', metasite = 'f'
        WHERE id = %(WBAN)s and network = 'USCRN'
        """,
            row,
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    main()
