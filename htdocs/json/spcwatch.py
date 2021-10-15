"""
 Return GeoJSON of valid watches for a provided timestamp or just now
"""
import datetime
import json

import memcache
import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape


def pointquery(lon, lat):
    """Do a query for stuff"""
    postgis = get_dbconn("postgis")
    cursor = postgis.cursor()

    res = dict(
        type="FeatureCollection",
        crs=dict(
            type="EPSG", properties=dict(code=4326, coordinate_order=[1, 0])
        ),
        features=[],
    )

    cursor.execute(
        """
    SELECT sel, issued at time zone 'UTC', expired at time zone 'UTC', type,
    ST_AsGeoJSON(geom), num from watches
    where ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
    ORDER by issued DESC
    """,
        (lon, lat),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/watch/%s/ww%04i.html") % (
            row[1].year,
            row[5],
        )
        res["features"].append(
            dict(
                type="Feature",
                id=row[5],
                properties=dict(
                    spcurl=url,
                    year=row[1].year,
                    type=row[3],
                    number=row[5],
                    issue=row[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    expire=row[2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
                geometry=json.loads(row[4]),
            )
        )

    return json.dumps(res)


def dowork(valid):
    """Actually do stuff"""
    postgis = get_dbconn("postgis")
    cursor = postgis.cursor()

    res = dict(
        type="FeatureCollection",
        crs=dict(
            type="EPSG", properties=dict(code=4326, coordinate_order=[1, 0])
        ),
        features=[],
    )

    cursor.execute(
        """
    SELECT sel, issued at time zone 'UTC', expired at time zone 'UTC', type,
    ST_AsGeoJSON(geom), num from watches where issued <= %s and
    expired > %s
    """,
        (valid, valid),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/watch/%s/ww%04i.html") % (
            row[1].year,
            row[5],
        )
        res["features"].append(
            dict(
                type="Feature",
                id=row[5],
                properties=dict(
                    spcurl=url,
                    year=row[1].year,
                    type=row[3],
                    number=row[5],
                    issue=row[1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    expire=row[2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                ),
                geometry=json.loads(row[4]),
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ts = fields.get("ts", None)
    lat = float(fields.get("lat", 0))
    lon = float(fields.get("lon", 0))
    if ts is None:
        ts = datetime.datetime.utcnow()
    else:
        ts = datetime.datetime.strptime(ts, "%Y%m%d%H%M")
    ts = ts.replace(tzinfo=pytz.UTC)

    cb = fields.get("callback")

    if lat != 0 and lon != 0:
        mckey = f"/json/spcwatch/{lon:.4f}/{lat:.4f}"
    else:
        mckey = f"/json/spcwatch/{ts:%Y%m%d%H%M}"
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        if lat != 0 and lon != 0:
            res = pointquery(lon, lat)
        else:
            res = dowork(ts)
        mc.set(mckey, res)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/vnd.geo+json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
