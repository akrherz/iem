"""Ingest DOT RWIS Webcams.

RUN from RUN_10MIN.sh
"""
# stdlib
import json
import os
import ssl
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

# third party
import requests
import urllib3
from pyiem import util

LOG = util.logger()
URI = (
    "https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
    "RWIS_Camera_Info_View/FeatureServer/0/query?where=1%3D1&outFields=*&"
    "f=json"
)
CLOUD404 = "/mesonet/tmp/dotcloud404.txt"
# prevent things from the future.
CEILING = util.utc() + timedelta(minutes=30)


# https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session


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
        if url.find("Not_Available") > -1:
            LOG.debug("skipping %s %s %s", cam, valid, url)
            continue
        try:
            req = get_legacy_session().get(url, timeout=30)
        except requests.exceptions.Timeout:
            # Try again
            req = requests.get(url, timeout=60)
        if req.status_code == 404:
            LOG.debug("cloud 404 %s", url)
            with open(CLOUD404, "a", encoding="utf8") as fh:
                fh.write(f"{url}\n")
                continue
        if req.status_code != 200:
            LOG.info("Fetching %s resulted in status %s", url, req.status_code)
            continue
        tmpfd = tempfile.NamedTemporaryFile(mode="wb", delete=False)
        tmpfd.write(req.content)
        tmpfd.close()
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
        cmd = (
            f"pqinsert -p 'webcam {routes} {valid:%Y%m%d%H%M} "
            f"camera/stills/{cam}.jpg "
            f"camera/{cam}/{cam}_{valid:%Y%m%d%H%M}.jpg jpg' {tmpfd.name}"
        )
        with subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            stdout, stderr = proc.communicate()
            if stderr != b"" or stdout != b"":
                LOG.info("%s stdout: %s stderr: %s", cmd, stdout, stderr)
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
    pgconn = util.get_dbconn("mesosite")
    # Create a dictionary of current webcams
    cursor = pgconn.cursor()
    cursor.execute("select id from webcams where network = 'IDOT'")
    domain = [row[0] for row in cursor]
    cursor.close()

    # Fetch the REST service
    req = util.exponential_backoff(requests.get, URI, timeout=30)
    if req is None:
        LOG.info("Failed to fetch REST service, aborting.")
        return
    jobj = req.json()
    if "features" not in jobj:
        LOG.info(
            "Got status_code: %s, invalid result of: %s",
            req.status_code,
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
        mcursor.close()
        pgconn.commit()


if __name__ == "__main__":
    main()
