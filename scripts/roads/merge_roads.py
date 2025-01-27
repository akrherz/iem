"""Compare the REST service with our current database."""

from datetime import timedelta

import httpx
from ingest_roads_rest import LOG, URI
from pandas import read_sql
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import utc
from shapely.geometry import LineString, MultiLineString


def main():
    """Go Main, please"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            "SELECT idot_id, longname from roads_base "
            "where (archive_end is null or archive_end > now()) ",
            conn,
            index_col="idot_id",
        )
    LOG.info("found %s rows from roads_base", len(df.index))
    resp = httpx.get(URI, timeout=30)
    jobj = resp.json()
    archive_begin = utc()
    for feat in jobj["features"]:
        props = feat["attributes"]
        idot_id = props["SEGMENT_ID"]
        if idot_id in df.index:
            continue
        # Geometry is [[pt]] and we only have single segments
        path = MultiLineString([LineString(feat["geometry"]["paths"][0])])
        # segid is defined by the database insert
        major = props["ROUTE_NAME"].replace("US 61 Business", "US 61")
        minor = props["NAMEID"].split("--", 1)[1]
        (typ, num) = major.replace("-", " ").split()
        int1 = num if typ == "I" else None
        us1 = num if typ == "US" else None
        st1 = num if typ == "IA" else None
        if major == "Airline Highway":
            num = 0
        sys_id = props["ROUTE_RANK"]
        longname = props["LONG_NAME"]
        geom = (
            f"ST_Transform(ST_SetSrid(ST_GeomFromText('{path.wkt}'), 3857), "
            "26915)"
        )
        LOG.info("idot_id %s [%s] is new", idot_id, major)
        cursor.execute(
            f"""
            INSERT into roads_base (major, minor, us1, st1, int1, type,
            longname, geom, idot_id, archive_begin, archive_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, {geom},
            %s, %s, %s) RETURNING segid
        """,
            (
                major[:10],
                minor,
                us1,
                st1,
                int1,
                sys_id,
                longname,
                idot_id,
                archive_begin,
                archive_begin + timedelta(days=365),
            ),
        )
        segid = cursor.fetchone()[0]
        cursor.execute(
            """
            UPDATE roads_base
            SET simple_geom = ST_Simplify(geom, 0.01) WHERE segid = %s
        """,
            (segid,),
        )
        # Figure out which WFO this segment is in...
        cursor.execute(
            """
            SELECT u.wfo,
            ST_Distance(u.geom, ST_Transform(b.geom, 4326))
            from ugcs u, roads_base b WHERE
            substr(ugc, 1, 2) = 'IA' and b.segid = %s
            and u.end_ts is null ORDER by ST_Distance ASC
        """,
            (segid,),
        )
        wfo = cursor.fetchone()[0]
        cursor.execute(
            "UPDATE roads_base SET wfo = %s WHERE segid = %s", (wfo, segid)
        )
        # Add a roads_current entry, 85 is a hack
        cursor.execute(
            """
            INSERT into roads_current(segid, valid, cond_code)
            VALUES (%s, %s, 0)
        """,
            (segid, archive_begin),
        )
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
