""".. title:: US Drought Monitor GeoJSON

Return to `JSON Services </json/>`_

Documentation for /geojson/usdm.py
----------------------------------

This service returns a GeoJSON representation of the US Drought Monitor
for a given date.  The date is specified in the `date` parameter, which
should be in the format of `YYYY-MM-DD`.  If no date is provided, the
latest valid USDM is returned.

Changelog
---------

- 2024-08-09: Initial documentation release

Example Usage
-------------

Fetch the latest USDM:

https://mesonet.agron.iastate.edu/geojson/usdm.py

"""

import datetime
import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    date: datetime.date = Field(
        None, description="Date to query for, YYYY-MM-DD"
    )


def rectify_date(dt):
    """Convert this tstamp into something we can actually use

    if '', use max valid from database
    if between tuesday and thursday at 8 AM, go back to last week
    back to tuesday
    """
    if dt is None:
        with get_sqlalchemy_conn("postgis") as conn:
            # Go get the latest USDM stored in the database!
            res = conn.execute(text("SELECT max(valid) from usdm"))
            res = res.fetchone()[0]
        return res

    offset = (dt.weekday() - 1) % 7
    return dt - datetime.timedelta(days=offset)


def run(ts):
    """Actually do the hard work of getting the USDM in geojson"""
    utcnow = utc()
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(
                "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
                "from usdm WHERE valid = :ts ORDER by dm ASC"
            ),
            {"ts": ts},
        )
        if res.rowcount == 0:
            # go back one week
            res = conn.execute(
                text(
                    "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
                    "from usdm WHERE valid = :ts ORDER by dm ASC"
                ),
                {"ts": ts - datetime.timedelta(days=7)},
            )

        data = {
            "type": "FeatureCollection",
            "features": [],
            "generation_time": utcnow.strftime(ISO8601),
            "count": res.rowcount,
        }
        for row in res:
            row = row._asdict()
            data["features"].append(
                dict(
                    type="Feature",
                    id=row["dm"],
                    properties=dict(
                        date=row["valid"].strftime("%Y-%m-%d"), dm=row["dm"]
                    ),
                    geometry=json.loads(row["geojson"]),
                )
            )
    return json.dumps(data)


def get_mckey(environ):
    """Get the key."""
    return f"/geojson/usdm.geojson|{environ['date']}"


@iemapp(
    help=__doc__,
    memcacheexpire=3600,
    memcachekey=get_mckey,
    schema=Schema,
    content_type="application/vnd.geo+json",
)
def application(environ, start_response):
    """Main Workflow"""
    headers = [("Content-type", "application/vnd.geo+json")]

    ts = rectify_date(environ["date"])
    if ts is None:
        raise IncompleteWebRequest("No USDM data found.")
    res = run(ts)
    start_response("200 OK", headers)
    return res
