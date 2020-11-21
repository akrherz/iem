"""Ingest DOT RWIS Webcams.

RUN from RUN_10MIN.sh
"""
from datetime import datetime, timedelta, timezone
import os
import tempfile
import subprocess

# third party
import requests
import pyiem.util as util

LOG = util.logger()
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "RWIS_Camera_Info_View/FeatureServer/0/query?where=1%3D1&outFields=*&"
    "f=json"
)


def process_feature(cursor, feat):
    """Do what we need to do with this feature."""
    props = feat["attributes"]
    rpuid = int(props["RPUID"])
    scene = int(props["SCANWEB_POSITIONID"])
    # Imagery is stored as IDOT-<RPUID:03i>-<SCENE-02i>.jpg
    cam = f"IDOT-{rpuid:03.0f}-{scene:02.0f}"
    # Loop over 10 possible images found with this feature
    for i in range(1, 11):
        suffix = f"_{i}" if i > 1 else ""
        key = f"IMAGE_DATE{suffix}"
        timestamp = props.get(key)
        if timestamp is None:
            continue
        valid = datetime(1970, 1, 1) + timedelta(seconds=timestamp / 1000.0)
        valid = valid.replace(tzinfo=timezone.utc)
        LOG.debug("%s %s", cam, valid)
        # Do we have this image?
        cursor.execute(
            "SELECT drct from camera_log where valid = %s and cam = %s",
            (valid, cam),
        )
        if cursor.rowcount > 0:
            continue
        url = props[f"IMAGE_URL{suffix}"]
        req = requests.get(url, timeout=15)
        if req.status_code == 404:
            LOG.debug("cloud 404 %s", url)
            with open("/mesonet/tmp/dotcloud404.txt", "a") as fh:
                fh.write(f"{url}\n")
                continue
        if req.status_code != 200:
            LOG.info("Fetching %s resulted in status %s", url, req.status_code)
            continue
        tmpfd = tempfile.NamedTemporaryFile(mode="wb", delete=False)
        tmpfd.write(req.content)
        tmpfd.close()
        # Create log entry
        cursor.execute(
            "INSERT into camera_log(cam, valid, drct) VALUES (%s, %s, %s)",
            (cam, valid, 0),
        )
        # Get current entry
        cursor.execute(
            "SELECT valid from camera_current where cam = %s", (cam,)
        )
        if cursor.rowcount == 0:
            LOG.info("Creating camera_current entry for %s", cam)
            cursor.execute(
                "INSERT into camera_current(cam, valid, drct) "
                "VALUES (%s, %s, %s)",
                (cam, valid - timedelta(minutes=1), 0),
            )
            cursor.execute(
                "SELECT valid from camera_current where cam = %s", (cam,)
            )
        lastvalid = cursor.fetchone()[0]
        routes = "a"
        if valid > lastvalid:
            routes = "ac"
            cursor.execute(
                "UPDATE camera_current SET valid = %s where cam = %s",
                (valid, cam),
            )
        cmd = (
            "pqinsert -p 'webcam %s %s camera/stills/%s.jpg "
            "camera/%s/%s_%s.jpg jpg' %s"
        ) % (
            routes,
            valid.strftime("%Y%m%d%H%M"),
            cam,
            cam,
            cam,
            valid.strftime("%Y%m%d%H%M"),
            tmpfd.name,
        )
        LOG.debug(cmd)
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        proc.communicate()
        os.unlink(tmpfd.name)


def main():
    """Go Main Go"""
    pgconn = util.get_dbconn("mesosite")

    # Fetch the REST service
    req = util.exponential_backoff(requests.get, URI, timeout=30)
    if req is None:
        LOG.info("Failed to fetch REST service, aborting.")
        return
    jobj = req.json()
    for feat in jobj["features"]:
        mcursor = pgconn.cursor()
        try:
            process_feature(mcursor, feat)
        except Exception as exp:
            LOG.error(exp)
        mcursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
