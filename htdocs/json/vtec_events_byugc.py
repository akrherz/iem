""" Find VTEC events by a given UGC code. """
import datetime
import json
from io import BytesIO, StringIO

import pandas as pd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.util import get_sqlalchemy_conn, html_escape
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/#{row['iso_issued'][:4]}-O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_df(ugc, sdate, edate):
    """Answer the request!"""
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
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
            eventid, phenomena, significance, hvtec_nwsli, wfo, ugc
            from warnings WHERE ugc = %s and issue > %s
            and issue < %s ORDER by issue ASC
            """,
            conn,
            params=(ugc, sdate, edate),
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
            }
        )

    return json.dumps(res)


def parse_date(val):
    """convert string to date."""
    return datetime.datetime.strptime(val, "%Y/%m/%d")


@iemapp()
def application(environ, start_response):
    """Answer request."""
    ugc = environ.get("ugc", "IAC001")[:6]
    try:
        sdate = parse_date(environ.get("sdate", "1986/1/1"))
        edate = parse_date(environ.get("edate", "2099/1/1"))
    except Exception as exp:
        raise IncompleteWebRequest(str(exp))
    cb = environ.get("callback", None)
    fmt = environ.get("fmt", "json")

    df = get_df(ugc, sdate, edate)
    if fmt == "xlsx":
        fn = f"vtec_{ugc}_{sdate:%Y%m%d}_{edate:%Y%m%d}.xlsx"
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return [bio.getvalue()]
    if fmt == "csv":
        fn = f"vtec_{ugc}_{sdate:%Y%m%d}_{edate:%Y%m%d}.csv"
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", f"attachment; Filename={fn}"),
        ]
        start_response("200 OK", headers)
        bio = StringIO()
        df.to_csv(bio, index=False)
        return [bio.getvalue().encode("utf-8")]

    res = as_json(df)
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
