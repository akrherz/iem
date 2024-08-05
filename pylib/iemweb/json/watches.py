""".. title: SPC Watches Service

Return to `JSON Services </json/>`_

Documentation for /json/watches.py
----------------------------------

Changelog
---------

- 2024-08-05: Initial documentation update

Example Requests
----------------

Provide all 2024 watches

https://mesonet.agron.iastate.edu/json/watches.py?year=2024

Provide all 2024 PDS watches

https://mesonet.agron.iastate.edu/json/watches.py?year=2024&is_pds=1

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """see how we are called."""

    callback: str = Field(default=None, description="JSONP callback function")
    is_pds: bool = Field(default=False, description="Only PDS Watches")
    year: int = Field(default=2022, description="Year to limit to")


def run(conn, year, is_pds):
    """Generate data."""

    if is_pds:
        limiter = "w.is_pds"
    else:
        limiter = "extract(year from w.issued at time zone 'UTC') = :year"
    res = conn.execute(
        text(f"""
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
    """),
        {"year": year},
    )
    data = {"events": []}
    for row in res:
        row = row._asdict()
        data["events"].append(
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
    return json.dumps(data)


def mckey(environ):
    """Generate a cache key."""
    return f"/json/watch/{environ['is_pds']}/{environ['year']}"


@iemapp(help=__doc__, schema=Schema, memcachekey=mckey, memcacheexpire=600)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    with get_sqlalchemy_conn("postgis") as conn:
        return run(conn, environ["year"], environ["is_pds"])
