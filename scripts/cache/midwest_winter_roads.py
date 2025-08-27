"""Write a snapshot of the winter roads GeoJSON to disk.

Called from RUN_10_AFTER.sh
"""

import os
import subprocess
import tempfile

import httpx
from pyiem.util import utc

# This was found to be 14 MB and not include Iowa
URL = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "Midwest_Winter_Road_Conditions_View/FeatureServer/0/query?"
    "where=1%3D1&"
    "outFields=ROUTE_NAME,REPORT_UPDATED,ROAD_CONDITION&"
    "f=geojson&returnGeodetic=true&geometryPrecision=4"
)
# This was found to be 5 MB and includes Iowa
REAL_EARTH = "https://realearth.ssec.wisc.edu/api/shapes?products=ROADS-IADOT"


def main():
    """Go Main Go."""
    utcnow = utc().replace(minute=0)
    with httpx.Client() as client, tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        resp = client.get(REAL_EARTH)
        resp.raise_for_status()
        with open("temp.geojson", "w") as fp:
            fp.write(resp.text)
        name = "midwest_winter_roads"
        subprocess.call(
            [
                "pqinsert",
                "-i",
                "-p",
                (
                    f"data ac {utcnow:%Y%m%d%H%M} "
                    f"gis/geojson/{name}.geojson "
                    f"GIS/{name}/{name}_{utcnow:%H%M}.geojson "
                    "geojson"
                ),
                "temp.geojson",
            ]
        )


if __name__ == "__main__":
    main()
