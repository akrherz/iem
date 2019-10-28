#!/usr/bin/env python
"""SPC MCD service."""
import json

from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

ISO9660 = "%Y-%m-%dT%H:%MZ"


def dowork(count, sort):
    """ Actually do stuff"""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor()

    res = dict(mcds=[])

    cursor.execute(
        """
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        num,
        product_id, year,
        ST_Area(geom::geography) / 1000000. as area_sqkm
        from mcd WHERE not ST_isEmpty(geom)
        ORDER by area_sqkm """
        + sort
        + """ LIMIT %s
    """,
        (count,),
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
                area_sqkm=row[5],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    count = int(fields.get("count", 10))
    sort = fields.get("sort", "DESC").upper()
    if sort not in ["ASC", "DESC"]:
        return

    cb = fields.get("callback")

    res = dowork(count, sort)
    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
