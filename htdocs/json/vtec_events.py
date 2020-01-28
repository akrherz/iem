"""Listing of VTEC events for a WFO and year"""
import json

import memcache
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape, utc

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run(wfo, year, phenomena, significance, combo):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
      phenomena (str, optional): 2 character phenomena
      significance (str, optional): 1 character VTEC significance
      combo (int, optional): special one-offs
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    table = "warnings_%s" % (year,)
    sbwtable = "sbw_%s" % (year,)
    plimit = "phenomena is not null and significance is not null"
    orderby = "u.phenomena ASC, u.significance ASC, u.utc_issue ASC"
    if phenomena is not None and significance is not None:
        plimit = ("phenomena = '%s' and significance = '%s'") % (
            phenomena[:2],
            significance[0],
        )
    if combo == 1:
        plimit = (
            "phenomena in ('SV', 'TO', 'FF') and significance in ('W', 'A')"
        )
        orderby = "u.utc_issue ASC"
    cursor.execute(
        """
    WITH polyareas as (
        SELECT phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,2163)) / 1000000.0)::numeric,0) as area
        from """
        + sbwtable
        + """ WHERE
        wfo = %s and eventid is not null and
        """
        + plimit
        + """ and status = 'NEW'
    ), ugcareas as (
        SELECT
        round(sum(ST_area(
            ST_transform(u.geom,2163)) / 1000000.0)::numeric,0) as area,
        string_agg(u.name || ' ['||u.state||']', ', ') as locations,
        eventid, phenomena, significance,
        min(issue) at time zone 'UTC' as utc_issue,
        max(expire) at time zone 'UTC' as utc_expire,
        min(product_issue) at time zone 'UTC' as utc_product_issue,
        max(init_expire) at time zone 'UTC' as utc_init_expire,
        max(hvtec_nwsli) as nwsli,
        max(fcster) as fcster from
        """
        + table
        + """ w JOIN ugcs u on (w.gid = u.gid)
        WHERE w.wfo = %s and eventid is not null and
        """
        + plimit
        + """
        GROUP by phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid)
        ORDER by """
        + orderby
        + """
    """,
        (wfo, wfo),
    )
    res = {
        "wfo": wfo,
        "generated_at": utc().strftime(ISO9660),
        "year": year,
        "events": [],
    }
    for row in cursor:
        uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
            year,
            wfo,
            row["phenomena"],
            row["significance"],
            row["eventid"],
        )
        res["events"].append(
            dict(
                phenomena=row["phenomena"],
                significance=row["significance"],
                eventid=row["eventid"],
                hvtec_nwsli=row["nwsli"],
                area=float(row["myarea"]),
                locations=row["locations"],
                issue=row["utc_issue"].strftime(ISO9660),
                product_issue=row["utc_product_issue"].strftime(ISO9660),
                expire=row["utc_expire"].strftime(ISO9660),
                init_expire=row["utc_init_expire"].strftime(ISO9660),
                uri=uri,
                wfo=wfo,
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    wfo = fields.get("wfo", "MPX")
    if len(wfo) == 4:
        wfo = wfo[1:]
    year = int(fields.get("year", 2015))
    phenomena = fields.get("phenomena")
    significance = fields.get("significance")
    cb = fields.get("callback")
    combo = int(fields.get("combo", 0))

    mckey = "/json/vtec_events/%s/%s/%s/%s/%s" % (
        wfo,
        year,
        phenomena,
        significance,
        combo,
    )
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(wfo, year, phenomena, significance, combo)
        mc.set(mckey, res, 60)

    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
