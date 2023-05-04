"""Download tempwinds_aloft dataset"""
import datetime
from io import BytesIO, StringIO

import pandas as pd
import pytz
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_data(station, sts, ets, tz, na, fmt):
    """Go fetch data please"""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT *,
            to_char(obtime at time zone :tz, 'YYYY/MM/DD HH24:MI')
                as obtime2,
            to_char(ftime at time zone :tz, 'YYYY/MM/DD HH24:MI')
                as ftime2
            from alldata_tempwind_aloft WHERE ftime >= :sts and
            ftime <= :ets and station = :station ORDER by obtime, ftime"""
            ),
            conn,
            params={"sts": sts, "ets": ets, "station": station, "tz": tz},
        )
    df = df.drop(columns=["obtime", "ftime"]).rename(
        columns={"obtime2": "obtime", "ftime2": "ftime"}
    )
    cols = df.columns.values.tolist()
    cols.remove("ftime")
    cols.remove("obtime")
    cols.insert(1, "obtime")
    cols.insert(2, "ftime")
    df = df[cols].dropna(axis=1, how="all")
    if na != "blank":
        df = df.fillna(na)
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, "Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


def parse_dates(form):
    """Nicely resolve dates please."""
    sts = datetime.date(
        int(form.get("year1")), int(form.get("month1")), int(form.get("day1"))
    )
    ets = datetime.date(
        int(form.get("year2")), int(form.get("month2")), int(form.get("day2"))
    )
    return sts, ets


def application(environ, start_response):
    """See how we are called"""
    form = parse_formvars(environ)
    try:
        sts, ets = parse_dates(form)
    except Exception:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"Error while parsing provided dates, ensure they are valid."]

    fmt = form.get("format", "csv")
    tz = form.get("tz", "UTC")
    pytz.timezone(tz)
    station = form.get("station")[:4]
    na = form.get("na", "M")
    if na not in ["M", "None", "blank"]:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: Invalid `na` value provided. {M, None, blank}"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [get_data(station, sts, ets, tz, na, fmt).encode("ascii")]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", f"attachment; Filename={station}.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(station, sts, ets, tz, na, fmt)]
