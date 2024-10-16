""".. title:: Storm Based Warnings by Latitude and Longitude Point

Return to `API Services </api/#json>`_

Documentation for /json/sbw_by_point.py
---------------------------------------

Returns NWS Storm Based Warnings for a provided latitude and longitude point.

Changelog
---------

- 2024-10-16: Added ``buffer`` parameter to expand the search area around the
  provided point.  The units are in decimal degrees with a range limited
  between 0 and 1.
- 2024-07-23: Initial documentation update and migration to pydantic.

Examples
--------

Return all storm based warnings that were active at a given time for a given
latitude and longitude point.

https::/mesonet.agron.iastate.edu/json/sbw_by_point.py?lat=41.99&lon=-92.0\
&valid=2024-07-23T12:00:00Z

Return all storm based warnings for a given latitude and longitude point valid
during 2023 in Excel format.

https::/mesonet.agron.iastate.edu/json/sbw_by_point.py?lat=41.99&lon=-92.0\
&sdate=2023-01-01&edate=2024-01-01&fmt=xlsx

Same request, but in CSV format.

https::/mesonet.agron.iastate.edu/json/sbw_by_point.py?lat=41.99&lon=-92.0\
&sdate=2023-01-01&edate=2024-01-01&fmt=csv

Provide all storm based warnings for a point in Iowa and buffer this point by
0.5 degrees.

https::/mesonet.agron.iastate.edu/json/sbw_by_point.py?lat=41.99&lon=-92.0\
&buffer=0.5

"""

import datetime
import json
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    buffer: float = Field(
        0.0,
        description="Buffer in decimal degrees around point",
        ge=0,
        le=1,
    )
    fmt: str = Field("json", description="The format of the response")
    lat: float = Field(41.99, description="Latitude of point", ge=-90, le=90)
    lon: float = Field(
        -92.0, description="Longitude of point", ge=-180, le=180
    )
    sdate: datetime.date = Field(
        default=datetime.date(2002, 1, 1), description="Start Date"
    )
    edate: datetime.date = Field(
        default=datetime.date(2099, 1, 1), description="End Date"
    )
    valid: AwareDatetime = Field(
        default=None,
        description="If provided, only provide results valid at this time.",
    )

    @field_validator("sdate", "edate", mode="before")
    @classmethod
    def check_dates(cls, value):
        """Forgive some things."""
        if value is None:
            return None
        return datetime.datetime.strptime(
            value.replace("/", "-"), "%Y-%m-%d"
        ).date()


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/#{row['vtec_year']}-O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_events(environ):
    """Get Events"""
    data = {
        "sbws": [],
        "lon": environ["lon"],
        "lat": environ["lat"],
        "buffer": environ["buffer"],
        "valid": None,
    }
    data["generation_time"] = utc().strftime(ISO8601)
    valid_limiter = ""
    params = {
        "lon": environ["lon"],
        "lat": environ["lat"],
        "buffer": environ["buffer"],
        "sdate": environ["sdate"],
        "edate": environ["edate"],
        "valid": environ["valid"],
    }
    if environ["valid"] is not None:
        valid_limiter = " and issue <= :valid and expire > :valid "
        data["valid"] = environ["valid"].strftime(ISO8601)

    ptsql = "ST_Point(:lon, :lat, 4326)"
    if environ["buffer"] > 0:
        ptsql = "ST_Buffer(ST_Point(:lon, :lat, 4326), :buffer)"

    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
    select vtec_year, wfo, significance, phenomena,
    to_char(issue at time zone 'UTC',
                'YYYY-MM-DDThh24:MIZ') as iso_issued,
        to_char(expire at time zone 'UTC',
                'YYYY-MM-DDThh24:MIZ') as iso_expired,
    to_char(issue at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as issued,
        to_char(expire at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as expired,
        eventid,
    tml_direction, tml_sknt, hvtec_nwsli, windtag, hailtag, tornadotag,
    damagetag from sbw where status = 'NEW' and
    ST_Intersects(geom, {ptsql}) and issue > :sdate and expire < :edate
    {valid_limiter} ORDER by issue ASC
        """
            ),
            conn,
            params=params,
        )
    if df.empty:
        return data, df
    df = df.replace({np.nan: None})
    df["name"] = df[["phenomena", "significance"]].apply(
        lambda x: get_ps_string(x.iloc[0], x.iloc[1]), axis=1
    )
    df["ph_name"] = df["phenomena"].map(VTEC_PHENOMENA)
    df["sig_name"] = df["significance"].map(VTEC_SIGNIFICANCE)
    # Construct a URL
    df["url"] = df.apply(make_url, axis=1)
    return data, df


def to_json(data, df):
    """Make JSON."""
    for _, row in df.iterrows():
        data["sbws"].append(
            {
                "url": row["url"],
                "phenomena": row["phenomena"],
                "eventid": row["eventid"],
                "significance": row["significance"],
                "wfo": row["wfo"],
                "issue": row["iso_issued"],
                "expire": row["iso_expired"],
                "tml_direction": row["tml_direction"],
                "tml_sknt": row["tml_sknt"],
                "hvtec_nwsli": row["hvtec_nwsli"],
                "name": row["name"],
                "ph_name": row["ph_name"],
                "sig_name": row["sig_name"],
                "issue_windtag": row["windtag"],
                "issue_hailtag": row["hailtag"],
                "issue_tornadotag": row["tornadotag"],
                "issue_damagetag": row["damagetag"],
                "issue_tornadodamagetag": (
                    row["damagetag"] if row["phenomena"] == "TO" else None
                ),
                "issue_thunderstormdamagetag": (
                    row["damagetag"] if row["phenomena"] == "SV" else None
                ),
            }
        )
    return data


@iemapp(
    help=__doc__,
    schema=Schema,
    parse_times=False,
)
def application(environ, start_response):
    """Answer request."""

    fmt = environ["fmt"]
    data, df = get_events(environ)
    if fmt == "xlsx":
        fn = f"sbw_{environ['lat']:.4f}N_{0 - environ['lon']:.4f}W.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"sbw_{environ['lat']:.4f}N_{0 - environ['lon']:.4f}W.csv"
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
