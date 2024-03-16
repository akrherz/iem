""".. title:: Temperature and Wind Aloft Data Service

Documentation for /cgi-bin/request/tempwind_aloft.py
----------------------------------------------------

To be written.

"""

from io import BytesIO, StringIO

import pandas as pd
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import iemapp
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
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__)
def application(environ, start_response):
    """See how we are called"""

    fmt = environ.get("format", "csv")
    tz = environ.get("tz", "UTC")
    station = environ.get("station", "")[:4]
    if station == "":
        raise IncompleteWebRequest("GET parameter station= missing")
    na = environ.get("na", "M")
    if na not in ["M", "None", "blank"]:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: Invalid `na` value provided. {M, None, blank}"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            get_data(
                station, environ["sts"], environ["ets"], tz, na, fmt
            ).encode("ascii")
        ]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", f"attachment; Filename={station}.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(station, environ["sts"], environ["ets"], tz, na, fmt)]
