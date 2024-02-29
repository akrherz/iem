""" Find VTEC events by a given Lat / Lon pair """
import datetime
import json
from io import BytesIO, StringIO

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.nws.vtec import VTEC_PHENOMENA, VTEC_SIGNIFICANCE, get_ps_string
from pyiem.util import html_escape
from pyiem.webutil import iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def make_url(row):
    """Build URL."""
    return (
        f"/vtec/#{row['iso_issued'][:4]}-O-NEW-K{row['wfo']}-"
        f"{row['phenomena']}-{row['significance']}-{row['eventid']:04.0f}"
    )


def get_df(lon, lat, sdate, edate):
    """Generate a report of VTEC ETNs used for a WFO and year

    Args:
      wfo (str): 3 character WFO identifier
      year (int): year to run for
    """
    giswkt = f"POINT({lon} {lat})"
    with get_sqlalchemy_conn("postgis") as conn:
        df = pd.read_sql(
            """
        WITH myugcs as (
            select gid from ugcs where
            ST_Contains(geom, ST_SetSRID(ST_GeomFromEWKT(%s),4326))
        )
        SELECT
        to_char(issue at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
            as iso_issued,
        to_char(expire at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ')
            as iso_expired,
        to_char(issue at time zone 'UTC', 'YYYY-MM-DD hh24:MI') as issued,
        to_char(expire at time zone 'UTC', 'YYYY-MM-DD hh24:MI') as expired,
        eventid, phenomena, significance, wfo, hvtec_nwsli, w.ugc
        from warnings w JOIN myugcs u on (w.gid = u.gid) WHERE
        issue > %s and issue < %s ORDER by issue ASC
        """,
            conn,
            params=(giswkt, sdate, edate),
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


@iemapp()
def application(environ, start_response):
    """Answer request."""
    try:
        lat = float(environ.get("lat", 42.5))
        lon = float(environ.get("lon", -95.5))
        sdate = parse_date(environ.get("sdate", "1986-01-01"))
        edate = parse_date(environ.get("edate", "2099-01-01"))
    except Exception as exp:
        raise IncompleteWebRequest(str(exp))
    cb = environ.get("callback", None)
    fmt = environ.get("fmt", "json")

    df = get_df(lon, lat, sdate, edate)
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
    if cb is not None:
        res = f"{html_escape(cb)}({res})"

    headers = [("Content-type", "application/json")]
    start_response("200 OK", headers)
    return [res.encode("ascii")]
