""".. title:: SPC Outlook Service

Return to `JSON Services </json/>`_.

Documentation for /json/spcoutlook.py
-------------------------------------

This service provides access to the Storm Prediction Center's Convective
Outlook products.  The service is designed to be called with a latitude and
longitude point.

Changelog
---------

- 2024-07-09: Add csv and excel output formats
- 2024-07-17: Fix problems with CSV and Excel output, sigh.

"""

import datetime
import json
from io import BytesIO
from typing import Tuple
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.nws.products.spcpts import THRESHOLD_ORDER
from pyiem.reference import ISO8601
from pyiem.util import utc
from pyiem.webutil import CGIModel, iemapp
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
        42.0, description="Latitude of point in decimal degrees"
    )
    lon: float = Field(
        -95.0, description="Longitude of point in decimal degrees"
    )
    last: int = Field(0, description="Limit to last N outlooks, 0 for all")
    day: int = Field(1, description="Day to query for, 1-8")
    time: str = Field(
        None,
        description=(
            "Optional specification for a valid timestamp to query outlooks "
            "for.  This is either a ISO8601 timestamp or 'current' for now."
        ),
    )
    cat: str = Field("categorical", description="Categorical or probabilistic")


def get_order(threshold):
    """Lookup a threshold and get its rank, higher is more extreme"""
    if threshold not in THRESHOLD_ORDER:
        return -1
    return THRESHOLD_ORDER.index(threshold)


def process_df(watches: pd.DataFrame) -> pd.DataFrame:
    """Condition the dataframe."""
    if watches.empty:
        return watches
    watches["threshold_rank"] = watches["threshold"].apply(get_order)
    return watches


def dotime(time, lon, lat, day, cat) -> Tuple[pd.DataFrame, datetime.datetime]:
    """Query for Outlook based on some timestamp"""
    if time in ["", "current", "now"]:
        ts = utc()
        if day > 1:
            ts += datetime.timedelta(days=day - 1)
    else:
        # ISO formatting
        ts = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%MZ")
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))
    with get_sqlalchemy_conn("postgis") as conn:
        outlooks = pd.read_sql(
            text("""
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        product_issue at time zone 'UTC' as v,
        threshold, category from spc_outlooks where
        product_issue = (
            select product_issue from spc_outlook where
            issue <= :ts and expire > :ts and day = :day
            and outlook_type = 'C' ORDER by product_issue DESC LIMIT 1)
        and ST_Contains(geom, ST_Point(:lon, :lat, 4326))
        and day = :day and outlook_type = 'C' and category = :cat
        """),
            conn,
            params={"lon": lon, "lat": lat, "day": day, "cat": cat, "ts": ts},
            index_col=None,
        )
    return process_df(outlooks), ts


def dowork(lon, lat, day, cat) -> pd.DataFrame:
    """Actually do stuff"""
    with get_sqlalchemy_conn("postgis") as conn:
        # Need to compute SIGN seperately
        outlooks = pd.read_sql(
            text("""
        WITH data as (
            SELECT issue at time zone 'UTC' as i,
            expire at time zone 'UTC' as e,
            product_issue at time zone 'UTC' as v,
            o.threshold, category, t.priority,
            row_number() OVER (PARTITION by expire
                ORDER by priority DESC NULLS last, issue ASC) as rank
            from spc_outlooks o, spc_outlook_thresholds t
            where o.threshold = t.threshold and
            ST_Contains(geom, ST_Point(:lon, :lat, 4326))
            and day = :day and outlook_type = 'C' and category = :cat
            and o.threshold not in ('TSTM', 'SIGN') ORDER by issue DESC),
        agg as (
            select i, e, v, threshold, category from data where rank = 1),
        sign as (
            SELECT issue at time zone 'UTC' as i,
            expire at time zone 'UTC' as e,
            product_issue at time zone 'UTC' as v,
            threshold, category from spc_outlooks
            where ST_Contains(geom, ST_Point(:lon, :lat, 4326))
            and day = :day and outlook_type = 'C' and category = :cat
            and threshold = 'SIGN' ORDER by expire DESC, issue ASC LIMIT 1)

        (SELECT i, e, v, threshold, category from agg
        ORDER by e DESC, threshold desc) UNION ALL
        (SELECT i, e, v, threshold, category from sign
        ORDER by e DESC, threshold desc)
        """),
            conn,
            params={"lon": lon, "lat": lat, "day": day, "cat": cat},
        )
    return outlooks


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
    time = environ.get("time")
    cat = environ["cat"].upper()
    fmt = environ["fmt"]
    lon = environ["lon"]
    lat = environ["lat"]
    last = environ["last"]
    day = environ["day"]
    ts = None
    if time is not None:
        outlooks, ts = dotime(time, lon, lat, day, cat)
        if not outlooks.empty:
            outlooks = outlooks.iloc[[0]]
    else:
        outlooks = dowork(lon, lat, day, cat)

    if fmt == "json" and time is not None:
        res = {
            "generation_time": utc().strftime(ISO8601),
            "query_params": {
                "time": ts.strftime(ISO8601),
                "lon": lon,
                "lat": lat,
                "cat": cat,
                "day": day,
            },
            "outlook": {},
        }
        if not outlooks.empty:
            row0 = outlooks.iloc[0]
            res["outlook"] = {
                "threshold": row0["threshold"],
                "utc_product_issue": pd.Timestamp(row0["v"]).strftime(ISO8601),
                "utc_issue": pd.Timestamp(row0["i"]).strftime(ISO8601),
                "utc_expire": pd.Timestamp(row0["e"]).strftime(ISO8601),
            }
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return json.dumps(res)
    if fmt == "json":
        running = {}
        res = {"outlooks": []}
        for _, row in outlooks.iterrows():
            if last > 0:
                running.setdefault(row["threshold"], 0)
                running[row["threshold"]] += 1
                if running[row["threshold"]] > last:
                    continue
            res["outlooks"].append(
                dict(
                    day=day,
                    utc_issue=row["i"].strftime(ISO8601),
                    utc_expire=row["e"].strftime(ISO8601),
                    utc_product_issue=row["v"].strftime(ISO8601),
                    threshold=row["threshold"],
                    category=row["category"],
                )
            )
        headers = [("Content-type", "application/json")]
        start_response("200 OK", headers)
        return json.dumps(res)

    outlooks = outlooks.rename(
        columns={
            "i": "utc_issue",
            "e": "utc_expire",
            "v": "utc_product_issue",
        },
    )
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
