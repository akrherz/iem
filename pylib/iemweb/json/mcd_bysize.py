""".. title:: Storm Prediction Center Mesoscale Convective Discussions by Size

Return to `API Services </api/#json>`_

Documentation for /json/mcd_bysize.py
-------------------------------------

Simple service that returns SPC's MCDs sorted by size.

Changelog
---------

- 2024-07-29: Initital documentation release.

"""

import json

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

BASEURL = "https://www.spc.noaa.gov/products/md"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="Optional JSON(P) callback.")
    count: int = Field(
        default=10,
        description="Number of results to return.",
        ge=1,
        le=1000,
    )
    sort: str = Field(
        default="desc",
        description="how to sort the results,",
        pattern="^(asc|desc|ASC|DESC)$",
    )


def dowork(count, sort):
    """Actually do stuff"""

    data = dict(mcds=[])
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text(f"""
            SELECT issue at time zone 'UTC' as i,
            expire at time zone 'UTC' as e, num, product_id, year,
            ST_Area(geom::geography) / 1000000. as area_sqkm,
            concerning from mcd WHERE not ST_isEmpty(geom)
            ORDER by area_sqkm {sort} LIMIT :cnt
        """),
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
