"""Listing of VTEC PDS Warnings."""

import json

from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.util import html_escape, utc
from pyiem.webutil import iemapp
from pymemcache.client import Client


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
        and is_pds
        GROUP by year, wfo, eventid, phenomena, significance
        ORDER by utc_issue ASC
    """
    )
    res = {"generated_at": utc().strftime(ISO8601), "events": []}
    for row in cursor:
        uri = (
            f"/vtec/#{row['year']}-O-NEW-K{row['wfo']}-{row['phenomena']}-"
            f"{row['significance']}-{row['eventid']:04.0f}"
        )
        res["events"].append(
            dict(
                year=row["year"],
                phenomena=row["phenomena"],
                significance=row["significance"],
                eventid=row["eventid"],
                issue=row["utc_issue"].strftime(ISO8601),
                product_issue=row["utc_product_issue"].strftime(ISO8601),
                expire=row["utc_expire"].strftime(ISO8601),
                init_expire=row["utc_init_expire"].strftime(ISO8601),
                uri=uri,
                wfo=row["wfo"],
                states=row["states"],
            )
        )
    pgconn.close()
    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    cb = environ.get("callback", None)

    mckey = "/json/vtec_pds"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run()
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
