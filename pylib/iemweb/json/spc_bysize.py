""".. title:: SPC Outlooks Sorted by Size

Return to `API Services </api/#json>`_

Documentation for /json/spc_bysize.py
-------------------------------------

This service emits unofficial IEM accounting of SPC outlooks sorted by size.
This service is great at finding problems in the IEM archive :(  Attempts
are made to generate links to the SPC website, to confirm the entries listed.

Changelog
---------

- 2025-04-07: Added sort={asc|desc} to control sort order.
- 2024-08-14: Documentation Update

Example Requests
----------------

Get the largest day 3 slight risks since 2020

https://mesonet.agron.iastate.edu/json/spc_bysize.py\
?day=3&threshold=SLGT&category=CATEGORICAL&syear=2020

"""

import json
import time
from datetime import date, timedelta

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.nws.products.spcpts import imgsrc_from_row
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    category: str = Field("CATEGORICAL", description="SPC outlook category")
    day: int = Field(..., description="SPC outlook day to query")
    sort: str = Field(
        default="desc",
        description="how to sort the results,",
        pattern="^(asc|desc|ASC|DESC)$",
    )
    syear: int = Field(1987, description="Inclusive start year to query")
    threshold: str = Field(..., description="SPC outlook threshold to query")


@with_sqlalchemy_conn("postgis")
def dowork(environ, conn: Connection = None) -> str:
    """Actually do stuff"""

    data = {"generated_at": f"{utc():%Y-%m-%dT%H:%M:%SZ}", "outlooks": []}
    hits = []
    sts = time.perf_counter()
    res = conn.execute(
        sql_helper(
            """
        SELECT product_issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        ST_Area(st_transform(geom, 9311)) / 1000000. as area_sqkm, cycle,
        product_issue at time zone 'UTC' as product_issue, category, day
        from spc_outlooks WHERE outlook_type = :ot and
        day = :day and threshold = :threshold
        and category = :cat and issue > :sdate and geom is not null
        ORDER by area_sqkm {order} NULLS LAST LIMIT 100
    """,
            order="ASC" if environ["sort"].lower() == "asc" else "DESC",
        ),
        {
            "day": environ["day"],
            "threshold": environ["threshold"],
            "cat": environ["category"],
            "ot": "F" if environ["category"].startswith("F") else "C",
            "sdate": date(environ["syear"], 1, 1),
        },
    )
    data["query_time[s]"] = round(time.perf_counter() - sts, 2)
    for row in res.mappings():
        key = f"{row['e']:%Y%m%d}"
        if key in hits:
            continue
        hits.append(key)
        data["outlooks"].append(
            {
                "date": f"{(row['e'] - timedelta(hours=13)):%Y-%m-%d}",
                "issued": row["i"].strftime(ISO8601),
                "area_sqkm": round(row["area_sqkm"], 2),
                "imgsrc": imgsrc_from_row(row),
                "cycle": row["cycle"],
            }
        )
        if len(data["outlooks"]) >= 10:
            break
    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Figure out the key for this request."""
    return (
        f"/json/spc_bysize.json|{environ['category']}|{environ['day']}|"
        f"{environ['syear']}|{environ['threshold']}|{environ['sort']}"
    ).replace(" ", "")


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=300)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    res = dowork(environ)
    return res.encode("ascii")
