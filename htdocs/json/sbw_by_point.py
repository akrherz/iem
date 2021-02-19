"""
Get storm based warnings by lat lon point, optionally a time
"""
import sys
from io import BytesIO, StringIO
import json
import datetime

from paste.request import parse_formvars
from pyiem.util import get_dbconn, utc
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pandas.io.sql import read_sql

ISO = "%Y-%m-%dT%H:%M:%SZ"
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_events(ctx):
    """ Get Events """
    data = {"sbws": [], "lon": ctx["lon"], "lat": ctx["lat"], "valid": None}
    data["generation_time"] = utc().strftime(ISO)
    valid_limiter = ""
    if "valid" in ctx:
        valid_limiter = " and issue <= '%s+00' and expire > '%s' " % (
            ctx["valid"].strftime("%Y-%m-%d %H:%M"),
            ctx["valid"].strftime("%Y-%m-%d %H:%M"),
        )
        data["valid"] = ctx["valid"].strftime(ISO)

    pgconn = get_dbconn("postgis")
    df = read_sql(
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
  tornadodamagetag from sbw
  where status = 'NEW' and
  ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT('POINT(%s %s)'),4326)) and
  issue > '2005-10-01' {valid_limiter} ORDER by issue ASC
    """,
        pgconn,
        params=(ctx["lon"], ctx["lat"]),
    )
    if df.empty:
        return data, df
    df["name"] = df[["phenomena", "significance"]].apply(
        lambda x: get_ps_string(x[0], x[1]), axis=1
    )
    df["ph_name"] = df["phenomena"].map(VTEC_PHENOMENA)
    df["sig_name"] = df["significance"].map(VTEC_SIGNIFICANCE)
    return data, df


def to_json(data, df):
    """Make JSON."""
    for _, row in df.iterrows():
        data["sbws"].append(
            {
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
                "issue_tornadodamagetag": row["tornadodamagetag"],
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
    ctx["lat"] = float(fields.get("lat", 41.99))
    ctx["lon"] = float(fields.get("lon", -92.0))
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
        fn = "sbw_%.4fN_%.4fW.xlsx" % (ctx["lat"], 0 - ctx["lon"])
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=" + fn),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = "sbw_%.4fN_%.4fW.csv" % (ctx["lat"], 0 - ctx["lon"])
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
