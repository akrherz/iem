"""Hit up ESRIs elevation REST service to compute a station elevation

"""
import time
import sys

import requests
from pyiem.util import get_dbconn


def get_elevation(lon, lat):
    """Use arcgisonline"""
    req = requests.get(
        (
            "http://sampleserver4.arcgisonline.com/"
            "ArcGIS/rest/services/Elevation/ESRI_Elevation_World/"
            "MapServer/exts/ElevationsSOE/ElevationLayers/1/"
            "GetElevationAtLonLat?lon=%s&lat=%s&f=pjson"
        )
        % (lon, lat),
        timeout=30,
    )
    if req.status_code != 200:
        print("ERROR: %s" % (req.status_code,))
        return None
    return req.json()["elevation"]


def workflow():
    """Our work"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor()
    mcursor2 = pgconn.cursor()
    mcursor.execute(
        "SELECT network, ST_x(geom) as lon, ST_y(geom) as lat, elevation, id "
        "from stations WHERE (elevation < -990 or elevation is null)"
    )

    for row in mcursor:
        elev = row[3]
        lat = row[2]
        lon = row[1]
        sid = row[4]
        network = row[0]
        newelev = get_elevation(lon, lat)

        print("%7s %s OLD: %s NEW: %.3f" % (sid, network, elev, newelev))
        mcursor2.execute(
            "UPDATE stations SET elevation = %s WHERE id = %s "
            "and network = %s",
            (newelev, sid, network),
        )
        time.sleep(2)

    mcursor2.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    if len(argv) == 1:
        workflow()
    else:
        print(get_elevation(argv[1], argv[2]))


if __name__ == "__main__":
    main(sys.argv)
