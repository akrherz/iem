"""Listing of SPC Watches."""
import json

import psycopg2.extras
from paste.request import parse_formvars
from pyiem.util import get_dbconn, html_escape
from pymemcache.client import Client

ISO9660 = "%Y-%m-%dT%H:%M:%SZ"


def run(year, is_pds):
    """Generate data."""
    pgconn = get_dbconn("postgis")
    cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if is_pds:
        limiter = "w.is_pds"
    else:
        limiter = f"extract(year from w.issued at time zone 'UTC') = {year}"
    cursor.execute(
        f"""
        with data as (
            select w.ctid, string_agg(state_abbr, ',') as states
            from watches w, states s where {limiter} and
            st_intersects(w.geom, s.the_geom) and issued is not null
            and expired is not null GROUP by w.ctid)
        select extract(year from issued at time zone 'UTC')::int as year,
        num, type,
        issued at time zone 'UTC' as utc_issued,
        expired at time zone 'UTC' as utc_expired,
        product_id_sel, product_id_wwp, tornadoes_1m_strong,
        hail_1m_2inch, max_hail_size, max_wind_gust_knots, states, is_pds
        from data d JOIN watches w on (d.ctid = w.ctid) ORDER by issued ASC
    """
    )
    res = {"events": []}
    for row in cursor:
        res["events"].append(
            dict(
                year=row["year"],
                num=row["num"],
                type=row["type"],
                issue=row["utc_issued"].strftime(ISO9660),
                expire=row["utc_expired"].strftime(ISO9660),
                product_id_sel=row["product_id_sel"],
                product_id_wwp=row["product_id_wwp"],
                tornadoes_1m_strong=row["tornadoes_1m_strong"],
                hail_1m_2inch=row["hail_1m_2inch"],
                max_hail_size=row["max_hail_size"],
                max_wind_gust_knots=row["max_wind_gust_knots"],
                states=row["states"],
                is_pds=row["is_pds"],
            )
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    cb = fields.get("callback", None)
    is_pds = fields.get("is_pds", "0") == "1"
    year = int(fields.get("year", 2022))

    mckey = f"/json/watch/{is_pds}/{year}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        res = run(year, is_pds)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
