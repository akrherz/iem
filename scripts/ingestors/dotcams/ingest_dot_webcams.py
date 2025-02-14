"""Ingest DOT RWIS Webcams.

NOTE this uses a custom openssl.conf :/

OPENSSL_CONF=openssl.conf python ingest_dot_webcams.py

RUN from RUN_10MIN.sh
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import httpx
from pyiem.database import get_dbconn
from pyiem.util import exponential_backoff, logger, utc

LOG = logger()
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "RWIS_Camera_Info_View/FeatureServer/0/query?where=1%3D1&outFields=*&"
    "f=json"
)
CLOUD404 = "/mesonet/tmp/dotcloud404.txt"
# prevent things from the future.
CEILING = utc() + timedelta(minutes=30)


def add_entry(cursor, cam, props):
    """Add a database entry for this camera."""
    cursor.execute(
        "INSERT into webcams (id, name, pan0, online, network, sts, removed, "
        "state, geom, fullres) VALUES (%s, %s, 0, 't', 'IDOT', now(), 'f', "
        "'IA', (select geom from stations where network = 'IA_RWIS' and "
        "remote_id = %s LIMIT 1), '640x480')",
        (cam, props["IMAGE_NAME"], int(props["RPUID"])),
    )


def process_feature(cursor, domain, feat):
    """Do what we need to do with this feature."""
    props = feat["attributes"]
    if props["RPUID"] is None or props["CAMERA_POSITION"] is None:
        LOG.info("feature has no RPUID, skipping")
        return
    rpuid = int(props["RPUID"])
    # Previous ingest used SCANWEB_POSITIONID, which was one less than CP
    scene = int(props["CAMERA_POSITION"])
    # Imagery is stored as IDOT-<RPUID:03i>-<SCENE-02i>.jpg
    cam = f"IDOT-{rpuid:03.0f}-{scene:02.0f}"
    if cam not in domain:
        LOG.warning("cam %s not in domain, adding entry", cam)
        add_entry(cursor, cam, props)
        domain.append(cam)
    # Loop over 10 possible images found with this feature
    for i in range(1, 11):
        suffix = f"_{i}" if i > 1 else ""
        key = f"IMAGE_DATE{suffix}"
        timestamp = props.get(key)
        if timestamp is None:
            continue
        valid = datetime(1970, 1, 1) + timedelta(seconds=timestamp / 1000.0)
        # We drop the seconds information as we can't really deal with it yet
        valid = valid.replace(second=0, tzinfo=timezone.utc)
        if valid > CEILING:
            LOG.info("%s is in the future %s, skipping", cam, valid)
            continue
        LOG.info("%s %s %s", cam, valid, props[f"IMAGE_URL{suffix}"])
        # Do we have this image?
        cursor.execute(
            "SELECT drct from camera_log where valid = %s and cam = %s",
            (valid, cam),
        )
        if cursor.rowcount > 0:
            continue
        url = props[f"IMAGE_URL{suffix}"]
        if url is None or url.find("Not_Available") > -1:
            LOG.debug("skipping %s %s %s", cam, valid, url)
            continue
        try:
            resp = httpx.get(url, timeout=30)
        except httpx.TimeoutException:
            # Try again
            resp = httpx.get(url, timeout=60)
        if resp.status_code == 404:
            LOG.debug("cloud 404 %s", url)
            with open(CLOUD404, "a", encoding="utf8") as fh:
                fh.write(f"{url}\n")
                continue
        if resp.status_code != 200:
            LOG.info("Fetching %s result in status %s", url, resp.status_code)
            continue
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmpfd:
            tmpfd.write(resp.content)
        # Get current entry
        cursor.execute(
            "SELECT valid from camera_current where cam = %s", (cam,)
        )
        if cursor.rowcount == 0:
            LOG.warning("Creating camera_current entry for %s", cam)
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
        cmd = [
            "pqinsert",
            "-p",
            f"webcam {routes} {valid:%Y%m%d%H%M} camera/stills/{cam}.jpg "
            f"camera/{cam}/{cam}_{valid:%Y%m%d%H%M}.jpg jpg",
            tmpfd.name,
        ]
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            stdout, stderr = proc.communicate()
            if stderr != b"" or stdout != b"":
                LOG.info(
                    "%s stdout: %s stderr: %s", " ".join(cmd), stdout, stderr
                )
                continue
        os.unlink(tmpfd.name)
        # Create log entry
        cursor.execute(
            "INSERT into camera_log(cam, valid, drct) VALUES (%s, %s, %s)",
            (cam, valid, 0),
        )
        if valid > lastvalid:
            cursor.execute(
                "UPDATE camera_current SET valid = %s where cam = %s",
                (valid, cam),
            )


def main():
    """Go Main Go"""
    pgconn = get_dbconn("mesosite")
    # Create a dictionary of current webcams
    cursor = pgconn.cursor()
    cursor.execute("select id from webcams where network = 'IDOT'")
    domain = [row[0] for row in cursor]
    cursor.close()

    # Fetch the REST service
    resp = exponential_backoff(httpx.get, URI, timeout=30)
    if resp is None:
        LOG.info("Failed to fetch REST service, aborting.")
        return
    jobj = resp.json()
    if "features" not in jobj:
        LOG.info(
            "Got status_code: %s, invalid result of: %s",
            resp.status_code,
            json.dumps(jobj, sort_keys=True, indent=4, separators=(",", ": ")),
        )
        return
    LOG.info("len(features): %s", len(jobj["features"]))
    for feat in jobj["features"]:
        mcursor = pgconn.cursor()
        try:
            process_feature(mcursor, domain, feat)
        except Exception as exp:
            LOG.exception(exp)
            LOG.warning(feat)
        mcursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
