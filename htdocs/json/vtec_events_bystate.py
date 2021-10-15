"""Listing of VTEC events for state and year"""
import json

import memcache
import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run(state, year, phenomena, significance):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    limits = ["phenomena is not null", "significance is not null"]
    if phenomena != "__":
        limits[0] = f"phenomena = '{phenomena}'"
    if significance != "_":
        limits[1] = f"significance = '{significance}'"
    plimit = " and ".join(limits)
    cursor.execute(
        f"""
    WITH polyareas as (
        SELECT wfo, phenomena, significance, eventid, round((ST_area(
        ST_transform(geom,2163)) / 1000000.0)::numeric,0) as area
        from sbw_{year} s, states t WHERE
        ST_Overlaps(s.geom, t.the_geom) and
        t.state_abbr = %s and eventid is not null and {plimit}
        and status = 'NEW'
    ), ugcareas as (
        SELECT w.wfo,
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
        warnings_{year} w JOIN ugcs u on (w.gid = u.gid)
        WHERE substr(u.ugc, 1, 2) = %s and eventid is not null and {plimit}
        GROUP by w.wfo, phenomena, significance, eventid)

    SELECT u.*, coalesce(p.area, u.area) as myarea
    from ugcareas u LEFT JOIN polyareas p on
    (u.phenomena = p.phenomena and u.significance = p.significance
     and u.eventid = p.eventid and u.wfo = p.wfo)
        ORDER by u.phenomena ASC, u.significance ASC, u.utc_issue ASC
    """,
        (state, state),
    )
    res = {"state": state, "year": year, "events": []}
    for row in cursor:
        uri = "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
            year,
            row["wfo"],
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
                wfo=row["wfo"],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    state = fields.get("state", "IA")[:2]
    year = int(fields.get("year", 2015))
    phenomena = fields.get("phenomena", "__")[:2]
    significance = fields.get("significance", "_")[:1]
    cb = fields.get("callback")

    mckey = "/json/vtec_events_bystate/%s/%s/%s/%s" % (
        state,
        year,
        phenomena,
        significance,
    )
    mc = memcache.Client(["iem-memcached:11211"], debug=0)
    res = mc.get(mckey)
    if not res:
        res = run(state, year, phenomena, significance)
        mc.set(mckey, res, 60)

    if cb is None:
        data = res
    else:
        data = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
