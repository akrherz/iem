"""
Return GeoJSON of valid watches for a provided timestamp or just now
"""

import datetime
import json
from zoneinfo import ZoneInfo

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import CGIModel, iemapp
from pymemcache.client import Client


class Schema(CGIModel):
    """See how we are called."""

    ts: str = Field(
        None, description="The timestamp to query for", pattern="^[0-9]{12}$"
    )
    lat: float = Field(
        0,
        description="The latitude to query for",
    )
    lon: float = Field(
        0,
        description="The longitude to query for",
    )
    callback: str = Field(
        None, description="Callback function for JSONP output"
    )


def pointquery(lon, lat):
    """Do a query for stuff"""
    pgconn, cursor = get_dbconnc("postgis")

    res = dict(
        type="FeatureCollection",
        crs=dict(
            type="EPSG", properties=dict(code=4326, coordinate_order=[1, 0])
        ),
        features=[],
    )
    cursor.execute(
        """
    SELECT sel, issued at time zone 'UTC' as ii,
    expired at time zone 'UTC' as ee, type, ST_AsGeoJSON(geom) as geo, num
    from watches where ST_Contains(geom, ST_Point(%s, %s, 4326))
    ORDER by issued DESC
    """,
        (lon, lat),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/watch/%s/ww%04i.html") % (
            row["ii"].year,
            row["num"],
        )
        res["features"].append(
            dict(
                type="Feature",
                id=row["num"],
                properties=dict(
                    spcurl=url,
                    year=row["ii"].year,
                    type=row["type"],
                    number=row["num"],
                    issue=row["ii"].strftime(ISO8601),
                    expire=row["ee"].strftime(ISO8601),
                ),
                geometry=json.loads(row["geo"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


def dowork(valid):
    """Actually do stuff"""
    pgconn, cursor = get_dbconnc("postgis")

    res = dict(
        type="FeatureCollection",
        crs=dict(
            type="EPSG", properties=dict(code=4326, coordinate_order=[1, 0])
        ),
        features=[],
    )

    cursor.execute(
        """
    SELECT sel, issued at time zone 'UTC' as ii,
    expired at time zone 'UTC' as ee, type, ST_AsGeoJSON(geom) as geo, num
    from watches where issued <= %s and expired > %s
    """,
        (valid, valid),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/watch/%s/ww%04i.html") % (
            row["ii"].year,
            row["num"],
        )
        res["features"].append(
            dict(
                type="Feature",
                id=row["num"],
                properties=dict(
                    spcurl=url,
                    year=row["ii"].year,
                    type=row["type"],
                    number=row["num"],
                    issue=row["ii"].strftime(ISO8601),
                    expire=row["ee"].strftime(ISO8601),
                ),
                geometry=json.loads(row["geo"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    if environ["ts"] is None:
        ts = datetime.datetime.utcnow()
    else:
        ts = datetime.datetime.strptime(environ["ts"], "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=ZoneInfo("UTC"))

    cb = environ.get("callback")

    mckey = (
        f"/json/spcwatch/{environ['lon']:.4f}/{environ['lat']:.4f}/"
        f"{ts:%Y%m%d%H%M}"
    )
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        if environ["lon"] != 0 and environ["lat"] != 0:
            res = pointquery(environ["lon"], environ["lat"])
        else:
            res = dowork(ts)
        mc.set(mckey, res)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/vnd.geo+json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
