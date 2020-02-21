"""Process an one-off of SCAN + SNOTEL metadata"""
import pandas as pd
from pyiem.util import get_dbconn

pgconn = get_dbconn("mesosite", user="mesonet")
cursor = pgconn.cursor()

df = pd.read_csv("/tmp/SNOTEL.SCAN.metadata.txt", sep="|")
for _, row in df.iterrows():
    nwsli = row["NWSLI"]
    name = row["NAME                             ST    GROUP      "]
    tokens = name.replace("'", " ").strip().split()
    sname = " ".join(tokens[:-3]) + " " + tokens[-1]
    if len(tokens) < 3:
        continue
    state = tokens[-3]
    lat = row[" LAT    "]
    lon = row[" LON"]
    network = "%s_DCP" % (state,)
    country = "US"
    elev = row[" ELEV  "]

    sql = """INSERT into stations(id, name, network, country, state,
    plot_name, elevation, online, metasite, geom) VALUES ('%s', '%s', '%s',
    '%s', '%s', '%s', %s, 't', 'f', 'SRID=4326;POINT(%s %s)');
    """ % (
        nwsli,
        sname,
        network,
        country,
        state,
        sname,
        elev,
        lon,
        lat,
    )

    cursor.execute(
        """SELECT * from stations where id = %s and network = %s
    """,
        (nwsli, network),
    )
    if cursor.rowcount == 0:
        cursor.execute(sql)
    else:
        cursor.execute(
            """UPDATE stations SET geom = 'SRID=4326;POINT(%s %s)',
        name = %s, elevation = %s WHERE id = %s and network = %s
        """,
            (lon, lat, sname, elev, nwsli, network),
        )

cursor.close()
pgconn.commit()
