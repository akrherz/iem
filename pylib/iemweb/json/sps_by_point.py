""".. title:: Special Weather Statements (SPS) by Point

Return to `API Services </api/#json>`_

This service returns any Special Weather Statements (SPS) that included a
polygon threat area.

Changelog
---------

- 2024-07-06: The `sdate` and `edate` parameters were rectified to be in the
  format of `YYYY-mm-dd` instead of `YYYY/mm/dd`.

Example Requests
----------------

Provide SPS metadata for those with a polygon that covered Newport, NC.

https://mesonet.agron.iastate.edu/json/sps_by_point.py?lat=34.77&lon=-76.88

Return the same, in Excel format this time and only those valid at 6z on
10 Aug 2024.

https://mesonet.agron.iastate.edu/json/sps_by_point.py\
?lat=34.77&lon=-76.88&valid=2024-08-10T06:00:00Z&fmt=xlsx

The same, but CSV this time

https://mesonet.agron.iastate.edu/json/sps_by_point.py\
?lat=34.77&lon=-76.88&valid=2024-08-10T06:00:00Z&fmt=csv

"""

import datetime
import json
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    fmt: str = Field(
        "json",
        pattern="^(json|csv|xlsx)$",
        description="The format of the output, either json, csv, or xlsx",
    )
    lat: float = Field(
        default=41.99, description="Latitude of point", ge=-90, le=90
    )
    lon: float = Field(
        default=-92.0, description="Longitude of point", ge=-180, le=180
    )
    sdate: datetime.date = Field(
        default=datetime.date(2002, 1, 1),
        description="Start date of search",
    )
    edate: datetime.date = Field(
        default=datetime.date(2099, 1, 1),
        description="End date of search",
    )
    valid: AwareDatetime = Field(
        default=None,
        description="If provided, only include events valid at this time.",
    )


def get_events(environ):
    """Get Events"""
    data = {
        "data": [],
        "lon": environ["lon"],
        "lat": environ["lat"],
        "valid": environ["valid"],
    }
    data["generation_time"] = utc().strftime(ISO8601)
    valid_limiter = ""
    params = {
        "lon": environ["lon"],
        "lat": environ["lat"],
        "sdate": environ["sdate"],
        "edate": environ["edate"],
        "valid": environ["valid"],
    }
    if environ["valid"] is not None:
        valid_limiter = " and issue <= :valid and expire > :valid "
        data["valid"] = environ["valid"].strftime(ISO8601)

    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
    select wfo, landspout, product_id, waterspout, max_hail_size,
    max_wind_gust,
    to_char(issue at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ') as issue,
    to_char(expire at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ') as expire
    from sps where
    ST_Contains(geom, ST_Point(:lon, :lat, 4326)) and
    issue > :sdate and expire < :edate
    {valid_limiter} ORDER by issue ASC
        """
            ),
            conn,
            params=params,
        )
    if df.empty:
        return data, df
    df = df.replace({np.nan: None})
    df["uri"] = "/p.php?pid=" + df["product_id"]
    return data, df


def to_json(data, df):
    """Make JSON."""
    for _, row in df.iterrows():
        data["data"].append(
            {
                "wfo": row["wfo"],
                "landspout": row["landspout"],
                "waterspout": row["waterspout"],
                "uri": row["uri"],
                "issue": row["issue"],
                "expire": row["expire"],
                "max_hail_size": row["max_hail_size"],
                "max_wind_gust": row["max_wind_gust"],
            }
        )
    return data


@iemapp(
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Answer request."""
    fmt = environ.get("fmt", "json")
    data, df = get_events(environ)
    if fmt == "xlsx":
        fn = f"sps_{environ['lat']:.4f}N_{(0 - environ['lon']):.4f}W.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"sps_{environ['lat']:.4f}N_{(0 - environ['lon']):.4f}W.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]
    res = to_json(data, df)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(res).encode("ascii")]
