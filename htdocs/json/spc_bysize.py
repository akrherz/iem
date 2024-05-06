"""SPC Outlook service."""

import json
from datetime import date, timedelta

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

BASEURL = "https://www.spc.noaa.gov/products/md"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    category: str = Field("CATEGORICAL", description="SPC outlook category")
    day: int = Field(..., description="SPC outlook day to query")
    syear: int = Field(1987, description="Inclusive start year to query")
    threshold: str = Field(..., description="SPC outlook threshold to query")


def dowork(environ):
    """Actually do stuff"""

    data = {"outlooks": []}
    hits = []
    with get_sqlalchemy_conn("postgis") as conn:
        res = conn.execute(
            text("""
            SELECT product_issue at time zone 'UTC' as i,
            expire at time zone 'UTC' as e,
            ST_Area(geom::geography) / 1000000. as area_sqkm
            from spc_outlooks WHERE outlook_type = :ot and
            day = :day and threshold = :threshold
            and category = :category and issue > :sdate
            ORDER by area_sqkm DESC NULLS LAST LIMIT 100
        """),
            {
                "day": environ["day"],
                "threshold": environ["threshold"],
                "category": environ["category"],
                "ot": "F" if environ["category"].startswith("F") else "C",
                "sdate": date(environ["syear"], 1, 1),
            },
        )
        for row in res:
            key = f"{row[1]:%Y%m%d}"
            if key in hits:
                continue
            hits.append(key)
            data["outlooks"].append(
                {
                    "date": f"{(row[1] - timedelta(hours=13)):%Y-%m-%d}",
                    "issued": row[0].strftime(ISO8601),
                    "area_sqkm": round(row[2], 2),
                }
            )
            if len(data["outlooks"]) >= 10:
                break

    return json.dumps(data)


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)

    cb = environ["callback"]

    res = dowork(environ)
    if cb is None:
        data = res
    else:
        data = f"{html_escape(cb)}({res})"

    return [data.encode("ascii")]
