"""
Get storm based warnings by lat lon point, optionally a time
"""
import datetime
import json
import sys
from io import BytesIO, StringIO

import numpy as np
from pandas.io.sql import read_sql
from paste.request import parse_formvars
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.util import get_sqlalchemy_conn, utc
from sqlalchemy import text

ISO = "%Y-%m-%dT%H:%M:%SZ"
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/#{row['iso_issued'][:4]}-O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_events(ctx):
    """Get Events"""
    data = {"sbws": [], "lon": ctx["lon"], "lat": ctx["lat"], "valid": None}
    data["generation_time"] = utc().strftime(ISO)
    valid_limiter = ""
    params = {
        "lon": ctx["lon"],
        "lat": ctx["lat"],
        "sdate": ctx["sdate"],
        "edate": ctx["edate"],
    }
    if "valid" in ctx:
        valid_limiter = " and issue <= :valid and expire > :valid "
        data["valid"] = ctx["valid"].strftime(ISO)
        params["valid"] = ctx["valid"]

    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            text(
                f"""
    select wfo, significance, phenomena,
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
    ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(:lon :lat)'),4326)) and
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
    df["name"] = df[["phenomena", "significance"]].apply(
        lambda x: get_ps_string(x[0], x[1]), axis=1
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


def try_valid(ctx, fields):
    """See if a valid stamp is provided or not."""
    if fields.get("valid") is None:
        return
    # parse at least the YYYY-mm-ddTHH:MM
    ts = datetime.datetime.strptime(fields["valid"][:16], "%Y-%m-%dT%H:%M")
    ctx["valid"] = utc(ts.year, ts.month, ts.day, ts.hour, ts.minute)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ctx = {}
    try:
        ctx["lat"] = float(fields.get("lat", 41.99))
        ctx["lon"] = float(fields.get("lon", -92.0))
        ctx["sdate"] = datetime.datetime.strptime(
            fields.get("sdate", "2002/1/1"), "%Y/%m/%d"
        )
        ctx["edate"] = datetime.datetime.strptime(
            fields.get("edate", "2099/1/1"), "%Y/%m/%d"
        )
    except ValueError:
        headers = [("Content-type", "text/plain")]
        start_response("404 File Not Found", headers)
        return [b"Failed to parse inputs."]

    fmt = fields.get("fmt", "json")
    try:
        try_valid(ctx, fields)
    except Exception as exp:
        sys.stderr.write(str(exp))
        headers = [("Content-type", "text/plain")]
        start_response("500 Internal Server Error", headers)
        return [b"Failed to parse valid, ensure YYYY-mm-ddTHH:MM:SSZ"]

    data, df = get_events(ctx)
    if fmt == "xlsx":
        fn = f"sbw_{ctx['lat']:.4f}N_{0 - ctx['lon']:.4f}W.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"sbw_{ctx['lat']:.4f}N_{0 - ctx['lon']:.4f}W.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; Filename=" + fn),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]
    res = to_json(data, df)
    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [json.dumps(res).encode("ascii")]
