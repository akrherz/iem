"""
Iowa DOT Truck dash camera imagery.  Save this to the IEM archives

/YYYY/mm/dd/camera/idot_trucks/keyhash/keyhash_timestamp.jpg
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import httpx
import pyproj
from pyiem.database import get_dbconn
from pyiem.util import exponential_backoff, logger

LOG = logger()
P3857 = pyproj.Proj("EPSG:3857")
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "AVL_Images_Past_1HR_View/FeatureServer/0/query?"
    "where=SECURE_PHOTO_URL+IS+NOT+NULL&resultRecordCount=1000&"
    "geometryType=esriGeometryEnvelope&"
    "spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&"
    "units=esriSRUnit_Meter&returnGeodetic=false&outFields=*&"
    "returnGeometry=true&multipatchOption=xyFootprint&"
    "applyVCSProjection=false&returnIdsOnly=false&returnUniqueIdsOnly=false&"
    "returnCountOnly=false&returnExtentOnly=false&returnDistinctValues=false&"
    "orderByFields=PHOTO_FILEDATE"
    "&returnZ=false&returnM=false&"
    "returnExceededLimitFeatures=true&quantizationParameters=&"
    "sqlFormat=none&f=json"
)


def get_current_fn(label):
    """Return how this is stored for current data"""
    return f"camera/idot_trucks/{label}.jpg"


def get_archive_fn(label, utc):
    """Return how this is stored for current data"""
    return f"camera/idot_trucks/{label}/{label}_{utc:%Y%m%d%H%M}.jpg"


def fetch_features(offset):
    """Fetch Features with the defined offset."""
    LOG.debug("fetch_features for offset: %s", offset)
    url = URI + f"&resultOffset={offset}"
    req = exponential_backoff(httpx.get, url, timeout=30)
    if req is None or req.status_code != 200:
        return False, []
    data = req.json()
    if "features" not in data:
        LOG.info(
            "Got status_code: %s, invalid result of: %s",
            req.status_code,
            json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")),
        )
        return False, []
    hasmore = data.get("exceededTransferLimit", False)
    return hasmore, data["features"]


def workflow():
    """Our workflow."""
    offset = 0
    while offset < 20000:
        hasmore, features = fetch_features(offset)
        process_features(features)
        offset += 1000
        if not hasmore:
            offset = 1e6


def process_features(features):
    """Do stuff"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute("SELECT label, valid from idot_dashcam_current")
    current = {}
    for row in cursor:
        current[row[0]] = row[1]

    for feat in features:
        # Major hack until upstream fixes the attributes
        url = feat["attributes"]["SECURE_PHOTO_URL"].replace("http:", "https:")
        # A32049-2025-04-01_13_48_49.jpg
        label, tstamp = url.split("/")[-1].removesuffix(".jpg").split("-", 1)
        valid = datetime.strptime(tstamp, "%Y-%m-%d_%H_%M_%S").replace(
            tzinfo=timezone.utc
        )
        if label not in current:
            current[label] = valid - timedelta(minutes=1)
            LOG.warning("Label %s is new", label)
        if valid <= current[label]:
            LOG.debug("valid: %s current: %s", valid, current[label])
            continue
        current[label] = valid
        LOG.info(
            "label: %s current: %s new: %s",
            label,
            current[label],
            valid,
        )
        req = exponential_backoff(httpx.get, url, timeout=15)
        if req is None or req.status_code != 200:
            LOG.info(
                "dot_truckcams.py dl fail |%s| %s",
                "req is None" if req is None else req.status_code,
                url,
            )
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(req.content)
        cmd = [
            "pqinsert",
            "-p",
            f"plot ac {valid:%Y%m%d%H%M} {get_current_fn(label)} "
            f"{get_archive_fn(label, valid)} jpg",
            tmp.name,
        ]
        with subprocess.Popen(cmd, stderr=subprocess.PIPE) as proc:
            proc.stderr.read()
        os.unlink(tmp.name)

        pt = P3857(feat["geometry"]["x"], feat["geometry"]["y"], inverse=True)
        # This table has an insert trigger that logs the entry as well
        cursor.execute(
            "INSERT into idot_dashcam_current(label, valid, "
            "geom) VALUES (%s, %s, ST_Point(%s, %s, 4326))",
            (label, valid, pt[0], pt[1]),
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    workflow()
