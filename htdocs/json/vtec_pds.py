"""Listing of VTEC PDS Warnings."""
import json

import memcache
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run():
    """Generate data."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute(
        """
        SELECT extract(year from issue) as year, wfo, eventid,
        phenomena, significance,
        min(product_issue at time zone 'UTC') as utc_product_issue,
        min(init_expire at time zone 'UTC') as utc_init_expire,
        min(issue at time zone 'UTC') as utc_issue,
        max(expire at time zone 'UTC') as utc_expire from warnings
        WHERE phenomena in ('TO', 'FF') and significance = 'W'
        and is_pds
        GROUP by year, wfo, eventid, phenomena, significance
        ORDER by utc_issue ASC
    """
    )
    res = {"events": []}
    for row in cursor:
        uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
            row["year"],
            row["wfo"],
            row["phenomena"],
            row["significance"],
            row["eventid"],
        )
        res["events"].append(
            dict(
                year=row["year"],
                phenomena=row["phenomena"],
                significance=row["significance"],
                eventid=row["eventid"],
                issue=row["utc_issue"].strftime(ISO9660),
                product_issue=row["utc_product_issue"].strftime(ISO9660),
                expire=row["utc_expire"].strftime(ISO9660),
                init_expire=row["utc_init_expire"].strftime(ISO9660),
                uri=uri,
                wfo=row["wfo"],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    cb = fields.get("callback", None)

    mckey = "/json/vtec_pds"
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 3600)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
