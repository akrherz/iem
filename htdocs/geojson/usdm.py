"""Generate a GeoJSON of US Drought Monitor"""

import datetime
import json

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.exceptions import IncompleteWebRequest
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp


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
        pgconn, cursor = get_dbconnc("postgis")
        # Go get the latest USDM stored in the database!
        cursor.execute("SELECT max(valid) from usdm")
        res = cursor.fetchone()["max"]
        cursor.close()
        pgconn.close()
        return res

    offset = (dt.weekday() - 1) % 7
    return dt - datetime.timedelta(days=offset)


def run(ts):
    """Actually do the hard work of getting the USDM in geojson"""
    pgconn, cursor = get_dbconnc("postgis")

    # Look for polygons into the future as well as we now have Flood products
    # with a start time in the future
    cursor.execute(
        "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
        "from usdm WHERE valid = %s ORDER by dm ASC",
        (ts,),
    )
    if cursor.rowcount == 0:
        # go back one week
        cursor.execute(
            "SELECT ST_asGeoJson(geom) as geojson, dm, valid "
            "from usdm WHERE valid = %s ORDER by dm ASC",
            (ts - datetime.timedelta(days=7),),
        )

    utcnow = datetime.datetime.utcnow()
    res = {
        "type": "FeatureCollection",
        "features": [],
        "generation_time": utcnow.strftime(ISO8601),
        "count": cursor.rowcount,
    }
    for row in cursor:
        res["features"].append(
            dict(
                type="Feature",
                id=row["dm"],
                properties=dict(
                    date=row["valid"].strftime("%Y-%m-%d"), dm=row["dm"]
                ),
                geometry=json.loads(row["geojson"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


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
        raise IncompleteWebRequest("No valid date provided")

    res = run(ts)
    start_response("200 OK", headers)
    return res
