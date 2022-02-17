""" Find VTEC events by a given UGC code. """
import json
from io import BytesIO, StringIO
import datetime

from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, html_escape
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pandas.io.sql import read_sql

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def make_url(row):
    """Build URL."""
    return "/vtec/#%s-O-NEW-K%s-%s-%s-%04i" % (
        row["iso_issued"][:4],
        row["wfo"],
        row["phenomena"],
        row["significance"],
        row["eventid"],
    )


def get_df(ugc, sdate, edate):
    """Answer the request!"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = read_sql(
            """
            SELECT
            to_char(issue at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as iso_issued,
            to_char(issue at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as issued,
            to_char(expire at time zone 'UTC',
                'YYYY-MM-DDThh24:MI:SSZ') as iso_expired,
            to_char(expire at time zone 'UTC',
                'YYYY-MM-DD hh24:MI') as expired,
            eventid, phenomena, significance, hvtec_nwsli, wfo
            from warnings WHERE ugc = %s and issue > %s
            and issue < %s ORDER by issue ASC
            """,
            conn,
            params=(ugc, sdate, edate),
        )
    if df.empty:
        return df
    df["name"] = df[["phenomena", "significance"]].apply(
        lambda x: get_ps_string(x[0], x[1]), axis=1
    )
    df["ph_name"] = df["phenomena"].map(VTEC_PHENOMENA)
    df["sig_name"] = df["significance"].map(VTEC_SIGNIFICANCE)
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
            }
        )

    return json.dumps(res)


def application(environ, start_response):
    """Answer request."""
    fields = parse_formvars(environ)
    ugc = fields.get("ugc", "IAC001")[:6]
    sdate = datetime.datetime.strptime(
        fields.get("sdate", "1986/1/1"), "%Y/%m/%d"
    )
    edate = datetime.datetime.strptime(
        fields.get("edate", "2099/1/1"), "%Y/%m/%d"
    )
    cb = fields.get("callback", None)
    fmt = fields.get("fmt", "json")

    df = get_df(ugc, sdate, edate)
    if fmt == "xlsx":
        fn = "vtec_%s_%s_%s.xlsx" % (
            ugc,
            sdate.strftime("%Y%m%d"),
            edate.strftime("%Y%m%d"),
        )
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=" + fn),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = "vtec_%s_%s_%s.csv" % (
            ugc,
            sdate.strftime("%Y%m%d"),
            edate.strftime("%Y%m%d"),
        )
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; Filename=" + fn),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = as_json(df)
    if cb is None:
        data = res
    else:
        data = "%s(%s)" % (html_escape(cb), res)

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [data.encode("ascii")]
