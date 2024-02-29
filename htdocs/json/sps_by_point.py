"""Get SPS by point."""

import datetime
import json
import sys
from io import BytesIO, StringIO

import numpy as np
import pandas as pd
from pyiem.reference import ISO8601
from pyiem.util import get_sqlalchemy_conn, utc
from pyiem.webutil import iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_events(ctx):
    """Get Events"""
    data = {"data": [], "lon": ctx["lon"], "lat": ctx["lat"], "valid": None}
    data["generation_time"] = utc().strftime(ISO8601)
    valid_limiter = ""
    params = {
        "lon": ctx["lon"],
        "lat": ctx["lat"],
        "sdate": ctx["sdate"],
        "edate": ctx["edate"],
    }
    if "valid" in ctx:
        valid_limiter = " and issue <= :valid and expire > :valid "
        data["valid"] = ctx["valid"].strftime(ISO8601)
        params["valid"] = ctx["valid"]

    params["giswkt"] = f"POINT({ctx['lon']} {ctx['lat']})"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            text(
                f"""
    select wfo, landspout, product_id, waterspout, max_hail_size,
    max_wind_gust,
    to_char(issue at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ') as issue,
    to_char(expire at time zone 'UTC', 'YYYY-MM-DDThh24:MIZ') as expire
    from sps where
    ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT(:giswkt),4326)) and
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


def try_valid(ctx, environ):
    """See if a valid stamp is provided or not."""
    if environ.get("valid") is None:
        return
    # parse at least the YYYY-mm-ddTHH:MM
    ts = datetime.datetime.strptime(environ["valid"][:16], "%Y-%m-%dT%H:%M")
    ctx["valid"] = utc(ts.year, ts.month, ts.day, ts.hour, ts.minute)


@iemapp()
def application(environ, start_response):
    """Answer request."""
    ctx = {}
    ctx["lat"] = float(environ.get("lat", 41.99))
    ctx["lon"] = float(environ.get("lon", -92.0))
    ctx["sdate"] = datetime.datetime.strptime(
        environ.get("sdate", "2002/1/1"), "%Y/%m/%d"
    )
    ctx["edate"] = datetime.datetime.strptime(
        environ.get("edate", "2099/1/1"), "%Y/%m/%d"
    )

    fmt = environ.get("fmt", "json")
    try:
        try_valid(ctx, environ)
    except Exception as exp:
        sys.stderr.write(str(exp))
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        return [b"Failed to parse valid, ensure YYYY-mm-ddTHH:MM:SSZ"]

    data, df = get_events(ctx)
    if fmt == "xlsx":
        fn = f"sps_{ctx['lat']:.4f}N_{(0 - ctx['lon']):.4f}W.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"sps_{ctx['lat']:.4f}N_{(0 - ctx['lon']):.4f}W.csv"
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
