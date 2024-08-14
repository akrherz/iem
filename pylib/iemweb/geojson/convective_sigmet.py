""".. title:: Convective SIGMET GeoJSON

Return to `API Services </api/#json>`_

This service provides a GeoJSON representation of current Convective SIGMETs.

Changelog
---------

- 2024-08-14: Documentation Update

Example Requests
----------------

Get the current Convective SIGMETs

https://mesonet.agron.iastate.edu/geojson/convective_sigmet.geojson

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")


def run():
    """Actually do the hard work of getting the current SBW in geojson"""
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(
                """
                SELECT *, ST_asGeoJson(geom) as geojson,
                issue at time zone 'UTC' as utc_issue,
                expire at time zone 'UTC' as utc_expire,
                label
                FROM sigmets_current WHERE sigmet_type = 'C'
                and expire > now()
                """
            )
        )

        data = {
            "type": "FeatureCollection",
            "features": [],
            "generation_time": utc().strftime(ISO8601),
            "count": res.rowcount,
        }
        for row in res:
            row = row._asdict()
            data["features"].append(
                dict(
                    type="Feature",
                    properties={
                        "issue": row["utc_issue"].strftime(ISO8601),
                        "expire": row["utc_expire"].strftime(ISO8601),
                        "label": row["label"],
                    },
                    geometry=json.loads(row["geojson"]),
                )
            )
    return json.dumps(data)


@iemapp(
    memcacheexpire=60,
    memcachekey="/geojson/convective_sigmet.geojson",
    content_type="application/vnd.geo+json",
    help=__doc__,
    schema=Schema,
)
def application(_environ, start_response):
    """Do Something"""
    # Go Main Go
    headers = [("Content-type", "application/vnd.geo+json")]

    res = run()
    start_response("200 OK", headers)
    return res.encode("ascii")
