#!/usr/bin/env python
"""geojson"""
import json
import sys
from pyiem.util import get_dbconn


def main():
    """Go Main"""
    dbconn = get_dbconn('scada')
    cursor = dbconn.cursor()

    sys.stdout.write("Content-type: application/vnd.geo+json\n\n")
    data = {"type": "FeatureCollection",
            "crs": {"type": "EPSG",
                    "properties": {"code": 4326,
                                   "coordinate_order": [1, 0]}},
            "features": []}
    cursor.execute("""SELECT lon, lat, 'n/a',
    'n/a', 'n/a', 'n/a', 'n/a', id from turbines""")
    for i, row in enumerate(cursor):
        data['features'].append({"type": "Feature", "id": i,
                                 "properties": {
                                    'id': row[7],
                                    'wakes': -1,
                                    'farmname': row[2],
                                    'expansion': row[3],
                                    'unitnumber': row[4],
                                    'farmnumber': row[5],
                                    'turbinename': row[6]
                                 },
                                 "geometry": {"type": "Point",
                                              "coordinates": [row[0],
                                                              row[1]]
                                              }
                                 })

    sys.stdout.write(json.dumps(data))


if __name__ == '__main__':
    main()
