"""Use the REST service to setup any new segments for the new season

 * JSON data is in Google 3857
"""
import sys
import json

from shapely.geometry import LineString, MultiLineString
import requests
from pyiem.util import get_dbconn

URI = (
    "https://iowadot.maps.arcgis.com/sharing/rest/content/items/"
    "5d6c7d6963e549539ead6e50d89bdd08/data"
)


def main():
    """Go Main, please"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    req = requests.get(URI, timeout=30)
    jobj = req.json()
    featureset = jobj["layers"][0]["featureSet"]
    for feat in featureset["features"]:
        props = feat["attributes"]
        # Geometry is [[pt]] and we only have single segments
        path = MultiLineString([LineString(feat["geometry"]["paths"][0])])
        # segid is defined by the database insert
        major = props["ROUTE_NAME"]
        (typ, _num) = major.replace("-", " ").split()
        if typ not in ["I", "US", "IA"]:
            print("Totally unknown, abort")
            print(json.dumps(jobj, indent=4))
            sys.exit()
        geom = (
            "ST_Transform(ST_SetSrid(ST_GeomFromText('%s'), 3857), 26915)"
        ) % (path.wkt)
        idot_id = props["SEGMENT_ID"]
        cursor.execute(
            """
        SELECT st_length(geom),
        st_length("""
            + geom
            + """), archive_begin from roads_base
        where idot_id = %s and archive_begin > '2017-01-01'::date
        ORDER by archive_begin DESC
        """,
            (idot_id,),
        )
        row = cursor.fetchone()
        if abs(row[1] - row[0]) > 1:
            print("%s, %s" % (str(row), cursor.rowcount))
            cursor.execute(
                """
            UPDATE roads_base SET geom = """
                + geom
                + """
            WHERE idot_id = %s and archive_begin > '2017-01-01'::date
            """,
                (idot_id,),
            )
            print("updated %s rows" % (cursor.rowcount,))

    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
