""".. title: SPC Watches Service

Return to `API Services </api/>`_

Documentation for /json/watches.py
----------------------------------

This service emits metadata for SPC issued convective watches.  You can request
one year's worth of data at a time.

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
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import Connection, text


class Schema(CGIModel):
    """see how we are called."""

    callback: Annotated[
        str | None, Field(description="JSONP callback function")
    ] = None
    is_pds: Annotated[bool, Field(description="Only PDS Watches")] = False
    year: Annotated[
        int, Field(description="Year to return watches for.", ge=1997)
    ] = 2022


def run(conn: Connection, year: int, is_pds: bool) -> str:
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
    data = {
        "generated_at": utc().strftime(ISO8601),
        "events": [],
    }
    for row in res.mappings():
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


def mckey(environ: dict) -> str:
    """Generate a cache key."""
    return f"/json/watch/{environ['is_pds']}/{environ['year']}"


@iemapp(help=__doc__, schema=Schema, memcachekey=mckey, memcacheexpire=600)
def application(environ: dict, start_response: callable):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    with get_sqlalchemy_conn("postgis") as conn:
        return run(conn, environ["year"], environ["is_pds"])
