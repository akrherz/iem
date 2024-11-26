""".. title:: SPC/WPC Outlook Progression by Point

Return to `API Services </api/#json>`_.

Documentation for /json/outlook_progression.py
-------------------------------------

This service requires a latitude and longitude point along with a date of
interest. The service will return the coincident SPC or WPC outlooks valid
for that date.

Implementation Notes
--------------------

1. In the case of hatching, two entries are returned per outlook per category.
2. Off cycle outlook updates are encoded as cycle=-1.
3. An attempt is made at the null / no outlook situation, but it is not
   perfect.

Changelog
---------

- 2024-11-26: Initial implementation

Example Usage
-------------

Provide the progression of convective outlooks for a point in Iowa for
21 May 2024.

https://mesonet.agron.iastate.edu/json/outlook_progression.py\
?lat=42&lon=-95&valid=2024-05-21&outlook_type=C

"""

import json
from datetime import date, timedelta
from io import BytesIO

import geopandas as gpd
import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from shapely.geometry import Point
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    fmt: str = Field(
        default="json",
        description="The format to return data in, either json, excel, or csv",
        pattern="^(json|excel|csv)$",
    )
    callback: str = Field(None, description="JSONP Callback Name")
    lat: float = Field(
        42.0,
        description="Latitude of point in decimal degrees",
        ge=20,
        le=60,
    )
    lon: float = Field(
        -95.0,
        description="Longitude of point in decimal degrees",
        ge=-130,
        le=-60,
    )
    outlook_type: str = Field(
        "C",
        description="Outlook type (C)onvective, (F)ire, (E)xcessive Rain",
        pattern="^(C|F|E)$",
    )
    valid: date = Field(
        ..., description="Date of interest in YYYY-MM-DD format"
    )


def dowork(environ: dict) -> pd.DataFrame:
    """Actually do stuff"""
    params = {
        "outlook_type": environ["outlook_type"],
        "sts": environ["valid"],
        "ets": environ["valid"] + timedelta(days=1),
    }
    with get_sqlalchemy_conn("postgis") as conn:
        # Figure out the outlooks for this date
        domain = pd.read_sql(
            text("""
        select day, cycle, issue, expire, product_issue from spc_outlook
        where issue > :sts and issue < :ets and outlook_type = :outlook_type
        order by product_issue asc
            """),
            conn,
            params=params,
        )
        domain["category"] = (
            "CATEGORICAL"
            if environ["outlook_type"] != "F"
            else "FIRE WEATHER CATEGORICAL"
        )
        # At the moment, something is messed up with postgis st_contains perf
        outlooks = gpd.read_postgis(
            text("""
        select o.day, o.geom, o.cycle, o.category, o.issue, o.expire,
        o.product_issue, o.threshold
        from spc_outlooks o
        where outlook_type = :outlook_type
        and issue > :sts and issue < :ets
        order by product_issue asc, category asc
        """),
            conn,
            params=params,
            geom_col="geom",
        )
    if domain.empty:
        return outlooks
    # Now we need to filter down to the ones that contain the point
    outlooks = outlooks[
        outlooks["geom"].contains(Point((environ["lon"], environ["lat"])))
    ]
    # Now we need to merge the domain into the outlooks
    rows = []
    for _, row in domain.iterrows():
        if outlooks[
            (outlooks["product_issue"] == row["product_issue"])
            & (outlooks["cycle"] == row["cycle"])
        ].empty:
            rows.append(row)
    if rows:
        outlooks = pd.concat([outlooks, pd.DataFrame(rows)], ignore_index=True)
    outlooks = outlooks.sort_values("product_issue", ascending=True)
    if not outlooks.empty:
        for col in ["issue", "expire", "product_issue"]:
            outlooks[col] = outlooks[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return outlooks.drop(columns=["geom"])


def get_ct(environ) -> str:
    """Figure out the content type."""
    fmt = environ["fmt"]
    if fmt == "json":
        return "application/json"
    if fmt == "excel":
        return "application/vnd.ms-excel"
    return "text/csv"


@iemapp(
    help=__doc__,
    schema=Schema,
    content_type=get_ct,
)
def application(environ, start_response):
    """Answer request."""
    fmt = environ["fmt"]
    outlooks = dowork(environ)

    if fmt == "json":
        res = {
            "generation_time": utc().strftime(ISO8601),
            "query_params": {
                "lon": environ["lon"],
                "lat": environ["lat"],
                "outlook_type": environ["outlook_type"],
                "valid": environ["valid"].strftime("%Y-%m-%d"),
            },
            "outlooks": outlooks.to_dict(orient="records"),
        }
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return json.dumps(res).replace("NaN", "null")
    if fmt == "excel":
        headers = [
            ("Content-type", "application/vnd.ms-excel"),
            ("Content-Disposition", "attachment; filename=outlooks.xls"),
        ]
        start_response("200 OK", headers)
        with BytesIO() as bio:
            outlooks.to_excel(bio, index=False)
            return bio.getvalue()

    headers = [
        ("Content-type", "text/csv"),
        ("Content-Disposition", "attachment; filename=outlooks.csv"),
    ]
    start_response("200 OK", headers)
    return outlooks.to_csv(index=False)
