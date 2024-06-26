"""Listing of SPC Watches."""

import json

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """see how we are called."""

    callback: str = Field(default=None, description="JSONP callback function")
    is_pds: bool = Field(default=False, description="Only PDS Watches")
    year: int = Field(default=2022, description="Year to limit to")


def run(year, is_pds):
    """Generate data."""
    pgconn, cursor = get_dbconnc("postgis")

    if is_pds:
        limiter = "w.is_pds"
    else:
        limiter = f"extract(year from w.issued at time zone 'UTC') = {year}"
    cursor.execute(
        f"""
        with data as (
            select w.ctid,
            string_agg(state_abbr, ',' order by state_abbr) as states
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
                issue=row["utc_issued"].strftime(ISO8601),
                expire=row["utc_expired"].strftime(ISO8601),
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
    pgconn.close()
    return json.dumps(res)


def mckey(environ):
    """Generate a cache key."""
    return f"/json/watch/{environ['is_pds']}/{environ['year']}"


@iemapp(help=__doc__, schema=Schema, memcachekey=mckey)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return run(environ["year"], environ["is_pds"])
