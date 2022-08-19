"""SPC MCD service."""
import os
import json

from pymemcache.client import Client
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

ISO9660 = "%Y-%m-%dT%H:%MZ"


def dowork(lon, lat):
    """Actually do stuff"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    res = dict(mcds=[])

    cursor.execute(
        """
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        num,
        product_id, year, concerning
        from mcd WHERE
        ST_Contains(geom, ST_GeomFromEWKT('SRID=4326;POINT(%s %s)'))
        ORDER by product_id DESC
    """,
        (lon, lat),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/md/%s/md%04i.html") % (
            row[4],
            row[2],
        )
        res["mcds"].append(
            dict(
                spcurl=url,
                year=row[4],
                utc_issue=row[0].strftime(ISO9660),
                utc_expire=row[1].strftime(ISO9660),
                product_num=row[2],
                product_id=row[3],
                concerning=row[5],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    lat = float(fields.get("lat", 42.0))
    lon = float(fields.get("lon", -95.0))

    cb = fields.get("callback", None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = ("/json/spcmcd/%.4f/%.4f") % (lon, lat)
    mc = Client(["iem-memcached", 11211])
    res = mc.get(mckey) if hostname != "iem.local" else None
    if not res:
        res = dowork(lon, lat)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
