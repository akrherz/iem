""".. title:: VTEC Events by UGC

Return to `API Services </api/#json>`_

Documentation for /json/vtec_events_byugc.py
--------------------------------------------

This metadata service returns VTEC events for the given UGC.

Changelog
---------

- 2026-06-25: Added `phenomena` and `significance` parameter to allow
  result filtering by a single VTEC event type.
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

Provide all Tornado Warnings for IAC169 during 2024

https://mesonet.agron.iastate.edu/json/vtec_events_byugc.py\
?ugc=IAC169&sdate=2024-01-01&edate=2024-12-31&phenomena=TO&significance=W

"""

import json
from datetime import datetime
from io import BytesIO, StringIO
from typing import Annotated
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import AwareDatetime, Field, model_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    CALLBACK_FIELD,
    VTEC_PH_FIELD_OPTIONAL,
    VTEC_SIG_FIELD_OPTIONAL,
)
from iemweb.mlib import rectify_wfo
from iemweb.util import json_response_dict

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    callback: CALLBACK_FIELD = None
    fmt: Annotated[
        str,
        Field(
            description="Response format, either json, csv, or excel",
            pattern="^(csv|json|excel|xlsx)$",
        ),
    ] = "json"
    edate: Annotated[
        str,
        Field(
            description="Inclusive End Date (US Central) for issuance",
        ),
    ] = f"{utc().year}-12-31"
    sdate: Annotated[
        str,
        Field(
            description=(
                "Start Date (midnight US Central) to start query for issuance"
            ),
        ),
    ] = "1980-01-01"
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
    )
    phenomena: VTEC_PH_FIELD_OPTIONAL = None
    significance: VTEC_SIG_FIELD_OPTIONAL = None

    @model_validator(mode="after")
    def ensure_both_ph_and_sig(self):
        """Ensure both phenomena and significance are provided if one is."""
        if (self.phenomena is not None and self.significance is None) or (
            self.phenomena is None and self.significance is not None
        ):
            raise ValueError(
                "Both phenomena and significance must be provided together"
            )
        return self

    @model_validator(mode="after")
    def ensure_sts_ets(self):
        """Rectify the parameter mess of what could be provided."""

        if self.sts is not None and self.ets is not None:
            return self
        for col in ["sdate", "edate"]:
            try:
                val = parse_date(getattr(self, col))
                if col == "edate":
                    val = val.replace(hour=23, minute=59, second=59)
                setattr(self, col, val)
            except Exception as exp:
                raise ValueError(
                    f"Invalid {col} provided: {getattr(self, col)}"
                ) from exp
        return self


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/?year={row['vtec_year']}&wfo={rectify_wfo(row['wfo'])}&"
        f"phenomena={row['phenomena']}&significance={row['significance']}&"
        f"eventid={row['eventid']:04.0f}"
    )


def get_df(query: Schema):
    """Answer the request!"""
    phsig_filter = ""
    if query.phenomena is not None and query.significance is not None:
        phsig_filter = (
            " and phenomena = :phenomena and significance = :significance "
        )
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            sql_helper(
                """
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
            and issue < :ets {phsig_filter} ORDER by issue ASC
            """,
                phsig_filter=phsig_filter,
            ),
            conn,
            params={
                "ugc": query.ugc,
                "sts": query.sts,
                "ets": query.ets,
                "phenomena": query.phenomena,
                "significance": query.significance,
            },
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
    res = json_response_dict({"events": []})
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

    return json.dumps(res).replace(" NaN", " null")


def parse_date(val: str) -> datetime:
    """convert string to date."""
    fmt = "%Y/%m/%d" if "/" in val else "%Y-%m-%d"
    return (
        datetime.strptime(val, fmt)
        .replace(tzinfo=ZoneInfo("America/Chicago"))
        .astimezone(ZoneInfo("UTC"))
    )


def get_mckey(environ):
    """Compute the key."""
    query: Schema = environ["_cgimodel_schema"]
    if query.fmt != "json":
        return None
    return (
        f"/json/vtec_events_byugc.json|{query.ugc}|"
        f"{query.sts}|{query.ets}|{query.phenomena}|"
        f"{query.significance}"
    ).replace(" ", "_")  # memcache key cannot have spaces


@iemapp(help=__doc__, schema=Schema, memcachekey=get_mckey, memcacheexpire=600)
def application(environ, start_response):
    """Answer request."""
    query: Schema = environ["_cgimodel_schema"]

    df = get_df(query)
    if query.fmt in ["xlsx", "excel"]:
        fn = f"vtec_{query.ugc}_{query.sts:%Y%m%d}_{query.ets:%Y%m%d}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        bio = BytesIO()
        df.to_excel(bio, index=False)
        start_response("200 OK", headers)
        return bio.getvalue()
    if query.fmt == "csv":
        fn = f"vtec_{query.ugc}_{query.sts:%Y%m%d}_{query.ets:%Y%m%d}.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        sio = StringIO()
        df.to_csv(sio, index=False)
        start_response("200 OK", headers)
        return sio.getvalue().encode()

    res = as_json(df).encode()
    start_response("200 OK", [("Content-type", "application/json")])
    return res
