"""
 Return GeoJSON of valid watches for a provided timestamp or just now
"""
import datetime
import json
from zoneinfo import ZoneInfo

import pandas as pd
from paste.request import parse_formvars
from pyiem.util import get_dbconnc, html_escape
from pymemcache.client import Client


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
                    issue=row["ii"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    expire=row["ee"].strftime("%Y-%m-%dT%H:%M:%SZ"),
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
                    issue=row["ii"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    expire=row["ee"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
                geometry=json.loads(row["geo"]),
            )
        )
    pgconn.close()
    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ts = fields.get("ts", None)
    lat = float(fields.get("lat", 0))
    lon = float(fields.get("lon", 0))
    if pd.isna([lat, lon]).any():
        lat, lon = 0, 0
    if ts is None:
        ts = datetime.datetime.utcnow()
    else:
        ts = datetime.datetime.strptime(ts, "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=ZoneInfo("UTC"))

    cb = fields.get("callback")

    if lat != 0 and lon != 0:
        mckey = f"/json/spcwatch/{lon:.4f}/{lat:.4f}"
    else:
        mckey = f"/json/spcwatch/{ts:%Y%m%d%H%M}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        if lat != 0 and lon != 0:
            res = pointquery(lon, lat)
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
