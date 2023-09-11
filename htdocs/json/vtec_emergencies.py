"""Listing of VTEC emergencies"""
import json

from paste.request import parse_formvars
from pyiem.util import get_dbconnc, html_escape
from pymemcache.client import Client

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run():
    """Generate data."""
    pgconn, cursor = get_dbconnc("postgis")

    cursor.execute(
        """
        SELECT extract(year from issue)::int as year, wfo, eventid,
        phenomena, significance,
        min(product_issue at time zone 'UTC') as utc_product_issue,
        min(init_expire at time zone 'UTC') as utc_init_expire,
        min(issue at time zone 'UTC') as utc_issue,
        max(expire at time zone 'UTC') as utc_expire,
        array_to_string(array_agg(distinct substr(ugc, 1, 2)), ',') as states
        from warnings
        WHERE phenomena in ('TO', 'FF') and significance = 'W'
        and is_emergency
        GROUP by year, wfo, eventid, phenomena, significance
        ORDER by utc_issue ASC
    """
    )
    res = {"events": []}
    for row in cursor:
        uri = (
            f"/vtec/#{row['year']}-O-NEW-K{row['wfo']}-"
            f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
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
                states=row["states"],
            )
        )
    pgconn.commit()
    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    cb = fields.get("callback", None)

    mckey = "/json/vtec_emergencies"
    mc = Client("iem-memcached:11211")
    data = mc.get(mckey)
    if data is not None:
        data = data.decode("utf-8")
    else:
        data = run()
        mc.set(mckey, data, 3600)
    mc.close()
    if cb is not None:
        data = f"{html_escape(cb)}({data})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
