"""Use the REST service to setup any new segments for the new season

* JSON data is in 3857
"""

import requests
from pyiem.util import get_dbconn
from shapely.geometry import LineString, MultiLineString

URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "511_IA_Road_Conditions_View/FeatureServer/0/query?"
    "where=1%3D1&objectIds=&time=&"
    "geometry=&geometryType=esriGeometryEnvelope&inSR=&"
    "spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&"
    "units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&"
    "returnGeometry=true&multipatchOption=xyFootprint&maxAllowableOffset="
    "&geometryPrecision=&outSR=&datumTransformation=&"
    "applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&"
    "returnCountOnly=false&returnExtentOnly=false&returnDistinctValues=false&"
    "orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&"
    "resultOffset=&resultRecordCount=&returnZ=false&returnM=false&"
    "returnExceededLimitFeatures=true&quantizationParameters=&"
    "sqlFormat=none&f=pjson&token="
)


def main():
    """Go Main, please"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()
    req = requests.get(URI, timeout=30)
    jobj = req.json()
    queue = []
    for feat in jobj["features"]:
        props = feat["attributes"]
        # Geometry is [[pt]] and we only have single segments
        path = MultiLineString([LineString(feat["geometry"]["paths"][0])])
        # segid is defined by the database insert
        geom = f"ST_Transform(ST_GeomFromText('{path.wkt}', 3857), 26915)"
        idot_id = props["SEGMENT_ID"]
        cursor.execute(
            f"""
        SELECT st_length(geom),
        st_length({geom}), archive_begin from roads_base
        where idot_id = %s and archive_end is null
        ORDER by archive_begin DESC
        """,
            (idot_id,),
        )
        row = cursor.fetchone()
        if row is None:
            print(f"{idot_id} is unknown to database!")
            queue.append(idot_id)
            continue
        if abs(row[1] - row[0]) > 1:
            print(str(row), cursor.rowcount)
            cursor.execute(
                f"""
            UPDATE roads_base SET geom = {geom}
            WHERE idot_id = %s and archive_end is null
            """,
                (idot_id,),
            )
            print(f"updated {cursor.rowcount} rows")

    print(queue)
    cursor.close()
    pgconn.commit()


if __name__ == "__main__":
    main()
