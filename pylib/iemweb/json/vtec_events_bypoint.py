""".. title:: VTEC Events by Point

Return to `API Services </api/#json>`_

Documentation for /json/vtec_events_bypoint.py
----------------------------------------------

This service returns VTEC event metadata for a given latitude and longitude
point.

Changelog
---------

- 2024-10-16: Added support for a ``buffer`` parameter.  The units are in
  decimal degrees with a range limited between 0 and 1.  This buffer is used
  to expand the search area around the provided point.
- 2024-08-08: Initial documentation and use pydantic

Example Usage
-------------

Get VTEC events for a point in Iowa

https://mesonet.agron.iastate.edu/json/vtec_events_bypoint.py?\
lat=41.99&lon=-93.61

Same request, but in Excel format

https://mesonet.agron.iastate.edu/json/vtec_events_bypoint.py?\
lat=41.99&lon=-93.61&fmt=xlsx

Same request, but in csv

https://mesonet.agron.iastate.edu/json/vtec_events_bypoint.py?\
lat=41.99&lon=-93.61&fmt=csv

Provide VTEC events for a point in Iowa and buffer this point by 0.5 degrees

https://mesonet.agron.iastate.edu/json/vtec_events_bypoint.py?\
lat=41.99&lon=-93.61&buffer=0.5

"""

import datetime
import json
from io import BytesIO, StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(None, description="JSONP callback function name")
    fmt: str = Field(
        default="json",
        description="The format to return the data in, either json or csv",
        pattern="^(json|csv|xlsx)$",
    )
    buffer: float = Field(
        0,
        description="Buffer in decimal degrees around the provided point",
        ge=0,
        le=1,
    )
    sdate: datetime.date = Field(
        datetime.date(1986, 1, 1), description="Start Date"
    )
    edate: datetime.date = Field(
        datetime.date(2099, 1, 1), description="End Date"
    )
    lat: float = Field(42.5, description="Latitude", ge=-90, le=90)
    lon: float = Field(-95.5, description="Longitude", ge=-180, le=180)


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/#{row['vtec_year']}-O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_df(lon, lat, sdate, edate, buffer: float):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    params = {
        "lon": lon,
        "lat": lat,
        "sdate": sdate,
        "edate": edate,
        "buffer": buffer,
    }
    ptsql = "ST_Point(:lon, :lat, 4326)"
    if buffer > 0:
        ptsql = "ST_Buffer(ST_Point(:lon, :lat, 4326), :buffer)"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(f"""
        WITH myugcs as (
            select gid from ugcs where ST_Intersects(geom, {ptsql})
        )
        SELECT vtec_year,
        to_char(issue at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
            as iso_issued,
        to_char(expire at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
            as iso_expired,
        to_char(issue at time zone 'UTC', 'YYYY-MM-DD hh24:MI') as issued,
        to_char(expire at time zone 'UTC', 'YYYY-MM-DD hh24:MI') as expired,
        eventid, phenomena, significance, wfo, hvtec_nwsli, w.ugc
        from warnings w JOIN myugcs u on (w.gid = u.gid) WHERE
        issue > :sdate and issue < :edate ORDER by issue ASC
        """),
            conn,
            params=params,
        )
    if df.empty:
        return df
    df["name"] = df[["phenomena", "significance"]].apply(
        lambda x: get_ps_string(x.iloc[0], x.iloc[1]), axis=1
    )
    df["ph_name"] = df["phenomena"].map(VTEC_PHENOMENA)
    df["sig_name"] = df["significance"].map(VTEC_SIGNIFICANCE)
    # Ugly hack for FW.A
    df.loc[
        (df["phenomena"] == "FW") & (df["significance"] == "A"), "ph_name"
    ] = "Fire Weather"
    # Construct a URL
    df["url"] = df.apply(make_url, axis=1)
    return df


def to_json(df):
    """Materialize as JSON."""
    res = {"events": []}
    for _, row in df.iterrows():
        res["events"].append(
            {
                "url": row["url"],
                "issue": row["iso_issued"],
                "expire": row["iso_expired"],
                "eventid": row["eventid"],
                "phenomena": row["phenomena"],
                "hvtec_nwsli": row["hvtec_nwsli"],
                "significance": row["significance"],
                "wfo": row["wfo"],
                "name": row["name"],
                "ph_name": row["ph_name"],
                "sig_name": row["sig_name"],
                "ugc": row["ugc"],
            }
        )

    return json.dumps(res)


def parse_date(val):
    """convert string to date."""
    fmt = "%Y/%m/%d" if "/" in val else "%Y-%m-%d"
    return datetime.datetime.strptime(val, fmt)


def get_mckey(environ: dict) -> str:
    """Construct the key."""
    return (
        f"/json/vtec_events_bypoint.py?lat={environ['lat']:.2f}&"
        f"lon={environ['lon']:.2f}&sdate={environ['sdate']:%Y-%m-%d}&"
        f"edate={environ['edate']:%Y-%m-%d}&fmt={environ['fmt']}&"
        f"buffer={environ['buffer']:.2f}"
    )


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=300)
def application(environ, start_response):
    """Answer request."""
    lat = environ["lat"]
    lon = environ["lon"]
    sdate = environ["sdate"]
    edate = environ["edate"]
    fmt = environ["fmt"]

    df = get_df(lon, lat, sdate, edate, environ["buffer"])
    if fmt == "xlsx":
        fn = (
            f"vtec_{(0 - lon):.4f}W_{lat:.4f}N_{sdate:%Y%m%d}_"
            f"{edate:%Y%m%d}.xlsx"
        )
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = (
            f"vtec_{(0 - lon):.4f}W_{lat:.4f}N_{sdate:%Y%m%d}_"
            f"{edate:%Y%m%d}.csv"
        )
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = to_json(df)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
