""".. title:: SPC MCD Service

Return to `JSON Services </json/>`_

Changelog
---------

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

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP Callback Name")
    fmt: str = Field(
        default="json",
        description="The format to return data in, either json, excel, or csv",
        pattern="^(json|excel|csv)$",
    )
    lat: float = Field(
        42.0,
        description="Latitude of point in decimal degrees",
        ge=-90,
        le=90,
    )
    lon: float = Field(
        -95.0,
        description="Longitude of point in decimal degrees",
        ge=-180,
        le=180,
    )


def dowork(lon, lat) -> pd.DataFrame:
    """Actually do stuff"""
    with get_sqlalchemy_conn("postgis") as conn:
        mcds = pd.read_sql(
            text("""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e, watch_confidence,
        num as product_num, product_id, year, concerning from mcd WHERE
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
            "https://mesonet.agron.iastate.edu/"
            "p.php?pid=" + mcds["product_id"]
        )
    return mcds.drop(columns=["i", "e"])


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]
    fmt = environ["fmt"]

    mcds = dowork(lon, lat)
    if fmt == "json":
        data = {"generated_at": utc().strftime(ISO8601), "mcds": []}
        for _, row in mcds.iterrows():
            conf = (
                None
                if pd.isna(row["watch_confidence"])
                else row["watch_confidence"]
            )
            data["mcds"].append(
                dict(
                    spcurl=row["spcurl"],
                    year=row["year"],
                    utc_issue=row["utc_issue"],
                    utc_expire=row["utc_expire"],
                    product_num=row["product_num"],
                    product_id=row["product_id"],
                    product_href=row["product_href"],
                    concerning=row["concerning"],
                    watch_confidence=conf,
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
