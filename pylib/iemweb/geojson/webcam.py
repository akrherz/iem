""".. title:: Webcam Metadata GeoJSON

Return to `API Services </api/#json>`_ listing.

Documentation for /geojson/webcam.py
------------------------------------

This service emits a geojson with metadata for webcam information that is
active at the given timestamp/now.

Changelog
---------

- 2024-06-30: Initial documentation release. Parameter `valid` added for
  consistency with other services.

Example Usage
-------------

Return current webcam information.

https://mesonet.agron.iastate.edu/geojson/webcam.geojson

"""

import json
from datetime import timezone

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    network: str = Field(
        default="KCCI",
        description="Network to query webcams for.",
    )
    ts: AwareDatetime = Field(
        default=None,
        description="Optional *legacy* timestamp to request webcams for.",
    )
    valid: AwareDatetime = Field(
        default=None,
        description="Optional timestamp to request webcams for.",
    )


def run(valid, network):
    """Actually do the hard work of getting the current SPS in geojson"""
    networks = [network]
    if network == "TV":
        networks = ["KCRG", "KCCI", "KELO", "ISUC", "MCFC"]
    params = {"networks": networks, "valid": valid}
    with get_sqlalchemy_conn("mesosite") as conn:
        if valid is None:
            res = conn.execute(
                text("""
                    SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
                    from camera_current c, webcams w
                    WHERE valid > (now() - '15 minutes'::interval)
                    and c.cam = w.id and
                    w.network = ANY(:networks)
                    ORDER by name ASC
            """),
                params,
            )
        else:
            res = conn.execute(
                text("""
                    SELECT *, ST_x(geom) as lon, ST_y(geom) as lat
                    from camera_log c, webcams w
                    WHERE valid = :valid and c.cam = w.id
                    and w.network = ANY(:networks) ORDER by name ASC
            """),
                params,
            )
        data = {
            "type": "FeatureCollection",
            "features": [],
            "valid_at": (valid if valid is not None else utc()).strftime(
                ISO8601
            ),
            "generated_at": utc().strftime(ISO8601),
            "count": res.rowcount,
        }

        for row in res.mappings():
            cv = row["valid"].astimezone(timezone.utc)
            url = (
                "https://mesonet.agron.iastate.edu/archive/data/"
                f"{cv:%Y/%m/%d}/camera/{row['cam']}/{row['cam']}_"
                f"{cv:%Y%m%d%H%M}.jpg"
            )
            data["features"].append(
                dict(
                    type="Feature",
                    id=row["id"],
                    properties={
                        "valid": cv.strftime(ISO8601),
                        "cid": row["id"],
                        "name": row["name"],
                        "county": row["county"],
                        "state": row["state"],
                        "angle": row["drct"],
                        "url": url,
                    },
                    geometry={
                        "type": "Point",
                        "coordinates": [row["lon"], row["lat"]],
                    },
                )
            )
    return json.dumps(data)


def get_mckey(environ):
    """Return a memcache key."""
    stamp = environ["valid"]
    if stamp is None:
        stamp = environ["ts"]
    if stamp is None:
        return "/geojson/webcam.geojson"
    return f"/geojson/webcam.geojson|{stamp:%Y%m%d%H%M}"


@iemapp(
    help=__doc__,
    schema=Schema,
    memcachekey=get_mckey,
    memcacheexpire=15,
    content_tye="application/vnd.geo+json",
)
def application(environ, start_response):
    """Do Main"""
    headers = [("Content-type", "application/vnd.geo+json")]

    stamp = environ["valid"]
    if stamp is None:
        stamp = environ["ts"]
    res = run(stamp, environ["network"])
    start_response("200 OK", headers)
    return res
