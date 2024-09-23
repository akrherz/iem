""".. title:: Special Weather Statement (SPS) GeoJSON

Return to `API Services </api/#json>`_ listing.

Documentation for /geojson/sps.py
---------------------------------

This service emits a geojson for a given valid time of NWS Special Weather
Statements (SPS) that contain polygons.

Changelog
---------

- 2024-06-30: Initial documentation release.

Example Usage
-------------

Return up to the moment SPSs with polygons.

https://mesonet.agron.iastate.edu/geojson/sps.py

Return SPSs valid at 20 UTC on 10 August 2024

https://mesonet.agron.iastate.edu/geojson/sps.py?valid=2024-08-10T20:00:00Z

"""

import json

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    valid: AwareDatetime = Field(
        default=utc(),
        description="Optional timestamp to request SPSs for.",
    )


def run(valid):
    """Actually do the hard work of getting the current SPS in geojson"""
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
            SELECT ST_asGeoJson(geom) as geojson, product_id,
            issue at time zone 'UTC' as utc_issue,
            expire at time zone 'UTC' as utc_expire
            from sps WHERE issue <= :valid and expire > :valid
            and not ST_IsEmpty(geom) and geom is not null
        """),
            {"valid": valid},
        )
        data = {
            "type": "FeatureCollection",
            "features": [],
            "valid_at": valid.strftime(ISO8601),
            "generated_at": utc().strftime(ISO8601),
            "count": res.rowcount,
        }

        for row in res.mappings():
            sts = row["utc_issue"].strftime(ISO8601)
            ets = row["utc_expire"].strftime(ISO8601)
            href = f"/api/1/nwstext/{row['product_id']}"
            data["features"].append(
                dict(
                    type="Feature",
                    id=row["product_id"],
                    properties=dict(href=href, issue=sts, expire=ets),
                    geometry=json.loads(row["geojson"]),
                )
            )
    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Return a memcache key."""
    return f"/geojson/sps.geojson|{environ['valid']:%Y%m%d%H%M}"


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

    res = run(environ["valid"])
    start_response("200 OK", headers)
    return res
