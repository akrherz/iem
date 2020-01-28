"""geojson"""
import json

from pyiem.util import get_dbconn


def application(_environ, start_response):
    """Go Main"""
    dbconn = get_dbconn("scada")
    cursor = dbconn.cursor()

    headers = [("Content-type", "application/vnd.geo+json")]
    start_response("200 OK", headers)
    data = {
        "type": "FeatureCollection",
        "crs": {
            "type": "EPSG",
            "properties": {"code": 4326, "coordinate_order": [1, 0]},
        },
        "features": [],
    }
    cursor.execute(
        """SELECT lon, lat, 'n/a',
    'n/a', 'n/a', 'n/a', 'n/a', id from turbines"""
    )
    for i, row in enumerate(cursor):
        data["features"].append(
            {
                "type": "Feature",
                "id": i,
                "properties": {
                    "id": row[7],
                    "wakes": -1,
                    "farmname": row[2],
                    "expansion": row[3],
                    "unitnumber": row[4],
                    "farmnumber": row[5],
                    "turbinename": row[6],
                },
                "geometry": {"type": "Point", "coordinates": [row[0], row[1]]},
            }
        )

    return [json.dumps(data).encode("ascii")]
