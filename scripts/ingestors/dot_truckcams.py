"""
  Iowa DOT Truck dash camera imagery.  Save this to the IEM archives

  /YYYY/mm/dd/camera/idot_trucks/keyhash/keyhash_timestamp.jpg
"""
import datetime
import subprocess
import tempfile
import os

import pytz
import requests
import pyproj
from pyiem.util import exponential_backoff, get_dbconn, logger

LOG = logger()
P3857 = pyproj.Proj(init="EPSG:3857")
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "AVL_Images_View/FeatureServer/0/query?where=1%3D1&objectIds=&time=&"
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


def get_current_fn(label):
    """ Return how this is stored for current data """
    return "camera/idot_trucks/%s.jpg" % (label,)


def get_archive_fn(label, utc):
    """ Return how this is stored for current data """
    return "camera/idot_trucks/%s/%s_%s.jpg" % (
        label,
        label,
        utc.strftime("%Y%m%d%H%M"),
    )


def workflow():
    """ Do stuff """
    req = exponential_backoff(requests.get, URI, timeout=30)
    if req is None or req.status_code != 200:
        return
    data = req.json()
    features = data.get("features", [])
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    cursor.execute("SELECT label, idnum from idot_dashcam_current")
    current = {}
    for row in cursor:
        current[row[0]] = row[1]

    for feat in features:
        logdt = feat["attributes"]["PHOTO_FILEDATE"]
        if logdt is None:
            continue
        ts = datetime.datetime.utcfromtimestamp(logdt / 1000.0)
        valid = ts.replace(tzinfo=pytz.UTC)
        label = feat["attributes"]["PHOTO_ANUMBER"]
        idnum = feat["attributes"]["PHOTO_UID"]
        if label is None:
            LOG.info("null label for PHOTO_UID: %s", idnum)
            continue
        if idnum <= current.get(label, 0):
            continue
        photourl = feat["attributes"]["PHOTO_URL"]
        # Go get the URL for saving!
        # print label, utc, feat['attributes']['PHOTO_URL']
        LOG.debug("Fetch %s", photourl)
        req = exponential_backoff(requests.get, photourl, timeout=15)
        if req is None or req.status_code != 200:
            LOG.info(
                "dot_truckcams.py dl fail |%s| %s",
                "req is None" if req is None else req.status_code,
                photourl,
            )
            continue
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(req.content)
        tmp.close()
        cmd = ("/home/ldm/bin/pqinsert -p 'plot ac %s %s %s jpg' %s") % (
            valid.strftime("%Y%m%d%H%M"),
            get_current_fn(label),
            get_archive_fn(label, valid),
            tmp.name,
        )
        proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        proc.stderr.read()
        os.unlink(tmp.name)

        pt = P3857(feat["geometry"]["x"], feat["geometry"]["y"], inverse=True)
        geom = "SRID=4326;POINT(%s %s)" % (pt[0], pt[1])
        # This table has an insert trigger that logs the entry as well
        cursor.execute(
            """
            INSERT into idot_dashcam_current(label, valid, idnum,
            geom) VALUES (%s, %s, %s, %s)
        """,
            (label, valid, idnum, geom),
        )

    cursor.close()
    pgconn.commit()
    pgconn.close()


if __name__ == "__main__":
    workflow()
