"""SCAN download backend."""

from io import StringIO

import pandas as pd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import ensure_list, iemapp
from sqlalchemy import text

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}


def get_df(stations, sts, ets):
    """Get what the database has!"""
    with get_sqlalchemy_conn("scan") as conn:
        df = pd.read_sql(
            text(
                "select * from alldata where station = ANY(:ids) and "
                "valid >= :sts and valid < :ets "
                "order by station asc, valid asc"
            ),
            conn,
            params={"ids": stations, "sts": sts, "ets": ets},
        )
    if not df.empty:
        df["valid"] = df["valid"].dt.strftime("%Y-%m-%d %H:%M")
    return df


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """
    Do something!
    """
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")
    stations = ensure_list(environ, "stations")
    varnames = ensure_list(environ, "vars")
    varnames.insert(0, "valid")
    varnames.insert(0, "station")
    what = environ.get("what", "dl")
    delimiter = DELIMITERS.get(environ.get("delim", "comma"))
    df = get_df(stations, environ["sts"], environ["ets"])
    if what in ["txt", "download"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=scan.txt"),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    sio = StringIO()
    df.to_csv(sio, index=False, sep=delimiter, columns=varnames)
    return [sio.getvalue().encode("ascii")]
