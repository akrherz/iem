""".. title:: VTEC Events by UGC

Return to `API Services </api/#json>`_

Documentation for /json/vtec_events_byugc.py
--------------------------------------------

This metadata service returns VTEC events for the given UGC.

Changelog
---------

- 2025-01-20: Added explicit `sts` and `ets` parameters for a more explicit
    datetime range.
- 2024-07-18: Initial documentation release and migration to pydantic.

Example Requests
----------------

Get all events for IAC169 during May 2024 UTC

https://mesonet.agron.iastate.edu/json/vtec_events_byugc.py\
?ugc=IAC169&sts=2024-05-01T00:00:00Z&ets=2024-06-01T00:00:00Z

Get all events during 2024 for Story County, Iowa IAC169

https://mesonet.agron.iastate.edu/json/vtec_events_byugc.py\
?ugc=IAC169&sdate=2024-01-01&edate=2024-12-31

Same request, but in CSV format

https://mesonet.agron.iastate.edu/json/vtec_events_byugc.py\
?ugc=IAC169&sdate=2024-01-01&edate=2024-12-31&fmt=csv

Same request, but in Excel format

https://mesonet.agron.iastate.edu/json/vtec_events_byugc.py\
?ugc=IAC169&sdate=2024-01-01&edate=2024-12-31&fmt=xlsx

"""

import json
from datetime import datetime
from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.mlib import rectify_wfo

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: str = Field(default=None, description="Optional JSON-P Callback")
    fmt: str = Field(
        default="json",
        description="Response format, either json, csv, or excel",
        pattern="^(csv|json|excel|xlsx)$",
    )
    edate: str = Field(
        default=f"{utc().year}-12-31",
        description="End Date (midnight US Central) to end query for issuance",
    )
    sdate: str = Field(
        default="1986-01-01",
        description=(
            "Start Date (midnight US Central) to start query for issuance"
        ),
    )
    sts: AwareDatetime = Field(
        default=None,
        description="Start timestamp (overrides sdate) for event issuance",
    )
    ets: AwareDatetime = Field(
        default=None,
        description="End timestamp (overrides edate) for event issuance",
    )
    ugc: str = Field(
        default="IAC001",
        description="6-character NWS Universal Geographic Code",
        pattern=r"^[A-Z][A-Z][CZ]\d\d\d$",
        max_length=6,
        min_length=6,
    )


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/?year={row['vtec_year']}&wfo={rectify_wfo(row['wfo'])}&"
        f"phenomena={row['phenomena']}&significance={row['significance']}&"
        f"eventid={row['eventid']:04.0f}"
    )


def get_df(ugc, sts: datetime, ets: datetime):
    """Answer the request!"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper("""
            SELECT vtec_year,
            to_char(issue at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
            to_char(issue at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as issued,
            to_char(expire at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
            to_char(expire at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as expired,
            eventid, phenomena, significance, hvtec_nwsli, wfo, ugc,
            product_ids[1] as product_id
            from warnings WHERE ugc = :ugc and issue >= :sts
            and issue < :ets ORDER by issue ASC
            """),
            conn,
            params={"ugc": ugc, "sts": sts, "ets": ets},
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


def as_json(df):
    """Materialize this df as JSON."""
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
                "product_id": row["product_id"],
            }
        )

    return json.dumps(res)


def parse_date(val):
    """convert string to date."""
    fmt = "%Y/%m/%d" if "/" in val else "%Y-%m-%d"
    return datetime.strptime(val, fmt)


def get_mckey(environ):
    """Compute the key."""
    if environ["fmt"] != "json":
        return None
    return (
        f"/json/vtec_events_byugc.json|{environ['ugc']}|"
        f"{environ['sdate']}|{environ['edate']}"
    ).replace(" ", "_")  # memcache key cannot have spaces


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=600)
def application(environ, start_response):
    """Answer request."""
    ugc = environ["ugc"]
    try:
        sts = parse_date(environ["sdate"])
        ets = parse_date(environ["edate"])
    except Exception as exp:
        raise IncompleteWebRequest(str(exp)) from exp
    if environ["sts"]:
        sts = environ["sts"]
    if environ["ets"]:
        ets = environ["ets"]
    fmt = environ["fmt"]

    df = get_df(ugc, sts, ets)
    if fmt in ["xlsx", "excel"]:
        fn = f"vtec_{ugc}_{sts:%Y%m%d}_{ets:%Y%m%d}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"vtec_{ugc}_{sts:%Y%m%d}_{ets:%Y%m%d}.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = as_json(df)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return res.encode("ascii")
