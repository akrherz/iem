""".. title:: WPC MPD Service

Return to `API Services </api/#json>`_

Changelog
---------

- 2025-06-29: Initial implementation of WPC MPD service.

Example Requests
----------------

Return MPDs issued for Ames, IA in JSON, then CSV, then Excel format.

https://mesonet.agron.iastate.edu/json/wpcmpd.py?lat=42.0&lon=-95.0

https://mesonet.agron.iastate.edu/json/wpcmpd.py?lat=42.0&lon=-95.0&fmt=csv

https://mesonet.agron.iastate.edu/json/wpcmpd.py?lat=42.0&lon=-95.0&fmt=excel

"""

import json
from io import BytesIO

import pandas as pd
from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection

from iemweb.fields import (
    CALLBACK_FIELD,
    LATITUDE_FIELD_OPTIONAL,
    LONGITUDE_FIELD_OPTIONAL,
)
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    fmt: str = Field(
        default="json",
        description="The format to return data in, either json, excel, or csv",
        pattern="^(json|excel|csv)$",
    )
    lat: LATITUDE_FIELD_OPTIONAL = 42.0
    lon: LONGITUDE_FIELD_OPTIONAL = -95.0


@with_sqlalchemy_conn("postgis")
def dowork(lon, lat, conn: Connection | None = None) -> pd.DataFrame:
    """Actually do stuff"""
    mpds = pd.read_sql(
        sql_helper("""
    SELECT issue at time zone 'UTC' as i,
    expire at time zone 'UTC' as e, watch_confidence,
    num as product_num, product_id, year, concerning,
    most_prob_tornado, most_prob_hail, most_prob_gust from mpd WHERE
    ST_Contains(geom, ST_Point(:lon, :lat, 4326))
    ORDER by product_id DESC
"""),
        conn,
        params={"lon": lon, "lat": lat},
    )
    if not mpds.empty:
        mpds["utc_issue"] = mpds["i"].dt.strftime(ISO8601)
        mpds["utc_expire"] = mpds["e"].dt.strftime(ISO8601)
        mpds["product_href"] = (
            "https://mesonet.agron.iastate.edu/p.php?pid=" + mpds["product_id"]
        )
    return mpds.drop(columns=["i", "e"])


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]
    fmt = environ["fmt"]

    mpds = dowork(lon, lat)
    if fmt == "json":
        data = json_response_dict({"mpds": []})
        for _, row in mpds.iterrows():
            conf = (
                None
                if pd.isna(row["watch_confidence"])
                else row["watch_confidence"]
            )
            data["mpds"].append(
                dict(
                    year=row["year"],
                    utc_issue=row["utc_issue"],
                    utc_expire=row["utc_expire"],
                    product_num=row["product_num"],
                    product_id=row["product_id"],
                    product_href=row["product_href"],
                    concerning=row["concerning"],
                    watch_confidence=conf,
                    most_prob_tornado=row["most_prob_tornado"],
                    most_prob_hail=row["most_prob_hail"],
                    most_prob_gust=row["most_prob_gust"],
                )
            )
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return json.dumps(data).encode("ascii")

    if fmt == "excel":
        headers = [
            ("Content-type", "application/vnd.ms-excel"),
            ("Content-Disposition", "attachment; filename=wpcmpd.xls"),
        ]
        start_response("200 OK", headers)
        with BytesIO() as bio:
            mpds.to_excel(bio, index=False)
            return bio.getvalue()

    headers = [
        ("Content-type", "text/csv"),
        ("Content-Disposition", "attachment; filename=wpcmpd.csv"),
    ]
    start_response("200 OK", headers)
    return mpds.to_csv(index=False).encode("ascii")
