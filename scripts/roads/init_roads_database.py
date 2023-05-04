"""Use the REST service to setup any new segments for the new season

 * JSON data is in Google 3857
"""

import requests
from ingest_roads_rest import LOG, URI
from pyiem.util import get_dbconn
from shapely.geometry import LineString, MultiLineString


def main():
    """Go Main, please"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    # cursor.execute("DELETE from roads_current")
    # LOG.info("removed %s rows from roads_current", cursor.rowcount)
    req = requests.get(URI, timeout=30)
    jobj = req.json()
    archive_begin = "2022-12-20 12:00"
    LOG.info("adding %s rows to roads_base", len(jobj["features"]))
    for feat in jobj["features"]:
        props = feat["attributes"]
        # Geometry is [[pt]] and we only have single segments
        path = MultiLineString([LineString(feat["geometry"]["paths"][0])])
        # segid is defined by the database insert
        major = props["ROUTE_NAME"]
        minor = props["NAMEID"].split("--", 1)[1].strip()
        (typ, num) = major.replace("-", " ").split()[:2]
        int1 = num if typ == "I" else None
        us1 = num if typ == "US" else None
        st1 = num if typ == "IA" else None
        if major == "Airline Highway":
            num = 0
        sys_id = props["ROUTE_RANK"]
        longname = props["LONG_NAME"]
        idot_id = props["SEGMENT_ID"]
        if idot_id != 505:
            continue
        print(props["NAMEID"])
        cursor.execute(
            """
            INSERT into roads_base (major, minor, us1, st1, int1, type,
            longname, geom, idot_id, archive_begin)
            VALUES (%s, %s, %s, %s, %s, %s, %s,
            ST_Transform(ST_SetSrid(ST_GeomFromText(%s), 3857), 26915),
            %s, %s) RETURNING segid
        """,
            (
                major[:10],
                minor,
                us1,
                st1,
                int1,
                sys_id,
                longname,
                path.wkt,
                idot_id,
                archive_begin,
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
