"""SPC Outlook service."""

import json
import time
from datetime import date, timedelta

from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.nws.products.spcpts import imgsrc_from_row
from pyiem.reference import ISO8601
from pyiem.util import html_escape, utc
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function")
    category: str = Field("CATEGORICAL", description="SPC outlook category")
    day: int = Field(..., description="SPC outlook day to query")
    syear: int = Field(1987, description="Inclusive start year to query")
    threshold: str = Field(..., description="SPC outlook threshold to query")


def dowork(environ):
    """Actually do stuff"""

    data = {"generated_at": f"{utc():%Y-%m-%dT%H:%M:%SZ}", "outlooks": []}
    hits = []
    dbconn, cursor = get_dbconnc("postgis")
    sts = time.perf_counter()
    cursor.execute(
        """
        SELECT product_issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        ST_Area(st_transform(geom, 9311)) / 1000000. as area_sqkm, cycle,
        product_issue at time zone 'UTC' as product_issue, category, day
        from spc_outlooks WHERE outlook_type = %(ot)s and
        day = %(day)s and threshold = %(threshold)s
        and category = %(category)s and issue > %(sdate)s and geom is not null
        ORDER by area_sqkm DESC NULLS LAST LIMIT 100
    """,
        {
            "day": environ["day"],
            "threshold": environ["threshold"],
            "category": environ["category"],
            "ot": "F" if environ["category"].startswith("F") else "C",
            "sdate": date(environ["syear"], 1, 1),
        },
    )
    data["query_time[s]"] = round(time.perf_counter() - sts, 2)
    for row in cursor:
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
    dbconn.close()
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
