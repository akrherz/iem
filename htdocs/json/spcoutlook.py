"""SPC Outlook JSON service."""

import datetime
import json
from zoneinfo import ZoneInfo

import pandas as pd
from pandas.io.sql import read_sql
from pyiem.database import get_dbconnc, get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.products.spcpts import THRESHOLD_ORDER
from pyiem.reference import ISO8601
from pyiem.util import html_escape
from pyiem.webutil import iemapp
from pymemcache.client import Client


def get_order(threshold):
    """Lookup a threshold and get its rank, higher is more extreme"""
    if threshold not in THRESHOLD_ORDER:
        return -1
    return THRESHOLD_ORDER.index(threshold)


def dotime(time, lon, lat, day, cat):
    """Query for Outlook based on some timestamp"""
    if time in ["", "current", "now"]:
        ts = datetime.datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        if day > 1:
            ts += datetime.timedelta(days=day - 1)
    else:
        # ISO formatting
        ts = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%MZ")
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            """
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        product_issue at time zone 'UTC' as v,
        threshold, category from spc_outlooks where
        product_issue = (
            select product_issue from spc_outlook where
            issue <= %s and expire > %s and day = %s
            and outlook_type = 'C' ORDER by product_issue DESC LIMIT 1)
        and ST_Contains(geom, ST_Point(%s, %s, 4326))
        and day = %s and outlook_type = 'C' and category = %s
        """,
            conn,
            params=(ts, ts, day, lon, lat, day, cat),
            index_col=None,
        )
    res = {
        "generation_time": datetime.datetime.utcnow().strftime(ISO8601),
        "query_params": {
            "time": ts.strftime(ISO8601),
            "lon": lon,
            "lat": lat,
            "cat": cat,
            "day": day,
        },
        "outlook": {},
    }
    if df.empty:
        return json.dumps(res)
    df["threshold_rank"] = df["threshold"].apply(get_order)
    df = df.sort_values("threshold_rank", ascending=False)
    res["outlook"] = {
        "threshold": df.iloc[0]["threshold"],
        "utc_product_issue": pd.Timestamp(df.iloc[0]["v"]).strftime(ISO8601),
        "utc_issue": pd.Timestamp(df.iloc[0]["i"]).strftime(ISO8601),
        "utc_expire": pd.Timestamp(df.iloc[0]["e"]).strftime(ISO8601),
    }
    return json.dumps(res)


def dowork(lon, lat, last, day, cat):
    """Actually do stuff"""
    pgconn, cursor = get_dbconnc("postgis")

    res = dict(outlooks=[])

    # Need to compute SIGN seperately
    cursor.execute(
        """
    WITH data as (
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        product_issue at time zone 'UTC' as v,
        o.threshold, category, t.priority,
        row_number() OVER (PARTITION by expire
            ORDER by priority DESC NULLS last, issue ASC) as rank
        from spc_outlooks o, spc_outlook_thresholds t
        where o.threshold = t.threshold and
        ST_Contains(geom, ST_Point(%s, %s, 4326))
        and day = %s and outlook_type = 'C' and category = %s
        and o.threshold not in ('TSTM', 'SIGN') ORDER by issue DESC),
    agg as (
        select i, e, v, threshold, category from data where rank = 1),
    sign as (
        SELECT issue at time zone 'UTC' as i,
        expire at time zone 'UTC' as e,
        product_issue at time zone 'UTC' as v,
        threshold, category from spc_outlooks
        where ST_Contains(geom, ST_Point(%s, %s, 4326))
        and day = %s and outlook_type = 'C' and category = %s
        and threshold = 'SIGN' ORDER by expire DESC, issue ASC LIMIT 1)

    (SELECT i, e, v, threshold, category from agg
    ORDER by e DESC, threshold desc) UNION ALL
    (SELECT i, e, v, threshold, category from sign
    ORDER by e DESC, threshold desc)
    """,
        (lon, lat, day, cat, lon, lat, day, cat),
    )
    running = {}
    for row in cursor:
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
    pgconn.close()
    return json.dumps(res)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    try:
        lat = float(environ.get("lat", 42.0))
        lon = float(environ.get("lon", -95.0))
        last = int(environ.get("last", 0))
        day = int(environ.get("day", 1))
    except ValueError as exp:
        raise IncompleteWebRequest(f"Invalid request parameter {exp}") from exp
    time = environ.get("time")
    cat = environ.get("cat", "categorical").upper()

    cb = environ.get("callback")

    mckey = f"/json/spcoutlook/{lon:.4f}/{lat:.4f}/{last}/{day}/{cat}/{time}"
    mc = Client("iem-memcached:11211")
    res = mc.get(mckey)
    if not res:
        if time is not None:
            res = dotime(time, lon, lat, day, cat)
        else:
            res = dowork(lon, lat, last, day, cat)
        mc.set(mckey, res, 3600)
    else:
        res = res.decode("utf-8")
    mc.close()

    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("utf-8")]
