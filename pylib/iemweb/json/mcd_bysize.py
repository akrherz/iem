""".. title:: Storm Prediction Center Mesoscale Convective Discussions by Size

Return to `API Services </api/#json>`_

Documentation for /json/mcd_bysize.py
-------------------------------------

Simple service that returns SPC's MCDs sorted by size.

Changelog
---------

- 2025-03-12: Added new Most Probable Intensity fields.
- 2024-07-29: Initital documentation release.

"""

import json
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

BASEURL = "https://www.spc.noaa.gov/products/md"


class Schema(CGIModel):
    """See how we are called."""

    callback: Annotated[
        str | None, Field(description="Optional JSON(P) callback.")
    ] = None
    count: Annotated[
        int,
        Field(
            description="Number of results to return.",
            ge=1,
            le=1000,
        ),
    ] = 10
    sort: Annotated[
        str,
        Field(
            description="how to sort the results,",
            pattern="^(asc|desc|ASC|DESC)$",
        ),
    ] = "desc"


def dowork(count, sort):
    """Actually do stuff"""

    data = {
        "mcds": [],
        "generated_at": utc().strftime(ISO8601),
    }
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            sql_helper(
                """
            SELECT issue at time zone 'UTC' as i,
            expire at time zone 'UTC' as e, num, product_id, year,
            ST_Area(geom::geography) / 1000000. as area_sqkm,
            concerning, most_prob_tornado, most_prob_hail, most_prob_gust
            from mcd WHERE not ST_isEmpty(geom)
            ORDER by area_sqkm {sort} LIMIT :cnt
        """,
                sort=sort,
            ),
            {"cnt": count},
        )
        for row in res:
            url = f"{BASEURL}/{row[4]}/md{row[2]:04.0f}.html"
            data["mcds"].append(
                dict(
                    spcurl=url,
                    year=row[4],
                    utc_issue=row[0].strftime(ISO8601),
                    utc_expire=row[1].strftime(ISO8601),
                    product_num=row[2],
                    product_id=row[3],
                    area_sqkm=row[5],
                    concerning=row[6],
                    most_prob_tornado=row[7],
                    most_prob_hail=row[8],
                    most_prob_gust=row[9],
                )
            )

    return json.dumps(data)


def get_mckey(environ: dict) -> str:
    """Get the key."""
    return f"/json/mcd_bysize.py?{environ['count']},{environ['sort']}"


@iemapp(help=__doc__, schema=Schema, memcacheexpire=600, memcachekey=get_mckey)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    count = environ["count"]
    sort = environ["sort"]
    return dowork(count, sort).encode("ascii")
