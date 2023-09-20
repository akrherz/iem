"""SPC MCD service."""
import json
import os

from paste.request import parse_formvars
from pyiem.util import get_dbconnc, html_escape
from pymemcache.client import Client

ISO9660 = "%Y-%m-%dT%H:%MZ"


def dowork(lon, lat):
    """Actually do stuff"""
    pgconn, cursor = get_dbconnc("postgis")

    res = {"mcds": []}

    cursor.execute(
        """
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        num,
        product_id, year, concerning
        from mcd WHERE
        ST_Contains(geom, ST_Point(%s, %s, 4326))
        ORDER by product_id DESC
    """,
        (lon, lat),
    )
    for row in cursor:
        url = ("https://www.spc.noaa.gov/products/md/%s/md%04i.html") % (
            row["year"],
            row["num"],
        )
        res["mcds"].append(
            dict(
                spcurl=url,
                year=row["year"],
                utc_issue=row["i"].strftime(ISO9660),
                utc_expire=row["e"].strftime(ISO9660),
                product_num=row["num"],
                product_id=row["product_id"],
                concerning=row["concerning"],
            )
        )
    pgconn.close()
    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    lat = float(fields.get("lat", 42.0))
    lon = float(fields.get("lon", -95.0))

    cb = fields.get("callback", None)

    hostname = os.environ.get("SERVER_NAME", "")
    mckey = ("/json/spcmcd/%.4f/%.4f") % (lon, lat)
    mc = Client("iem-memcached:11211")
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
