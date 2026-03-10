""".. title:: SPC MCD Service

Return to `API Services </api/#json>`_

Changelog
---------

- 2026-03-10: Prevent NaN values in the response.
- 2025-03-12: Added new Most Probable Intensity tags for MCDs
- 2024-07-09: Add csv and excel output formats

Example Requests
----------------

Return MCDs issued for Ames, IA in JSON, then CSV, then Excel format.

https://mesonet.agron.iastate.edu/json/spcmcd.py?lat=42.0&lon=-95.0

https://mesonet.agron.iastate.edu/json/spcmcd.py?lat=42.0&lon=-95.0&fmt=csv

https://mesonet.agron.iastate.edu/json/spcmcd.py?lat=42.0&lon=-95.0&fmt=excel

"""

import json
from io import BytesIO
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.reference import ISO8601
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    CALLBACK_FIELD,
    LATITUDE_FIELD,
    LONGITUDE_FIELD,
)
from iemweb.util import json_response_dict


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    fmt: Annotated[
        str,
        Field(
            description="The format to return, either json, excel, or csv",
            pattern="^(json|excel|csv)$",
        ),
    ] = "json"
    lat: LATITUDE_FIELD = 42.0
    lon: LONGITUDE_FIELD = -95.0


def dowork(lon, lat) -> pd.DataFrame:
    """Actually do stuff"""
    with get_sqlalchemy_conn("postgis") as conn:
        mcds = pd.read_sql(
            sql_helper("""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e, watch_confidence,
        num as product_num, product_id, year, concerning,
        most_prob_tornado, most_prob_hail, most_prob_gust from mcd WHERE
        ST_Contains(geom, ST_Point(:lon, :lat, 4326))
        ORDER by product_id DESC
    """),
            conn,
            params={"lon": lon, "lat": lat},
        )
    if not mcds.empty:
        mcds["spcurl"] = (
            "https://www.spc.noaa.gov/products/md/"
            + mcds["year"].astype(str)
            + "/md"
            + mcds["product_num"].apply(lambda x: f"{x:04.0f}")
            + ".html"
        )
        mcds["utc_issue"] = mcds["i"].dt.strftime(ISO8601)
        mcds["utc_expire"] = mcds["e"].dt.strftime(ISO8601)
        mcds["product_href"] = (
            "https://mesonet.agron.iastate.edu/p.php?pid=" + mcds["product_id"]
        )
    return mcds.drop(columns=["i", "e"])


def clean(value):
    """Prevent NaN."""
    return None if pd.isna(value) else value


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]
    fmt = environ["fmt"]

    mcds = dowork(lon, lat)
    if fmt == "json":
        data = json_response_dict({"mcds": []})
        for _, row in mcds.iterrows():
            data["mcds"].append(
                dict(
                    spcurl=row["spcurl"],
                    year=row["year"],
                    utc_issue=row["utc_issue"],
                    utc_expire=row["utc_expire"],
                    product_num=row["product_num"],
                    product_id=row["product_id"],
                    product_href=row["product_href"],
                    concerning=clean(row["concerning"]),
                    watch_confidence=clean(row["watch_confidence"]),
                    most_prob_tornado=clean(row["most_prob_tornado"]),
                    most_prob_hail=clean(row["most_prob_hail"]),
                    most_prob_gust=clean(row["most_prob_gust"]),
                )
            )
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return json.dumps(data).encode("ascii")

    if fmt == "excel":
        headers = [
            ("Content-type", "application/vnd.ms-excel"),
            ("Content-Disposition", "attachment; filename=spcmcd.xls"),
        ]
        start_response("200 OK", headers)
        with BytesIO() as bio:
            mcds.to_excel(bio, index=False)
            return bio.getvalue()

    headers = [
        ("Content-type", "text/csv"),
        ("Content-Disposition", "attachment; filename=spcmcd.csv"),
    ]
    start_response("200 OK", headers)
    return mcds.to_csv(index=False).encode("ascii")
