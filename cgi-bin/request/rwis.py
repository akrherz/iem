"""Download Interface for RWIS data"""
# pylint: disable=abstract-class-instantiated
from io import BytesIO, StringIO

import pandas as pd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import ensure_list, iemapp
from sqlalchemy import text

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@iemapp(default_tz="America/Chicago")
def application(environ, start_response):
    """Go do something"""
    include_latlon = environ.get("gis", "no").lower() == "yes"
    myvars = ensure_list(environ, "vars")
    myvars.insert(0, "station")
    myvars.insert(1, "obtime")
    delimiter = DELIMITERS.get(environ.get("delim", "comma"))
    what = environ.get("what", "dl")
    tzname = environ.get("tz", "UTC")
    src = environ.get("src", "atmos")
    stations = ensure_list(environ, "stations")
    if not stations:
        raise IncompleteWebRequest("Missing GET parameter stations=")

    tbl = "alldata"
    if src in ["soil", "traffic"]:
        tbl = f"alldata_{src}"
    network = environ.get("network", "IA_RWIS")
    nt = NetworkTable(network, only_online=False)
    if "_ALL" in stations:
        stations = list(nt.sts.keys())
    params = {
        "tzname": tzname,
        "ids": stations,
        "sts": environ["sts"],
        "ets": environ["ets"],
    }
    sql = text(
        f"SELECT *, valid at time zone :tzname as obtime from {tbl} "
        "WHERE station = ANY(:ids) and valid BETWEEN :sts and :ets "
        "ORDER by valid ASC"
    )
    with get_sqlalchemy_conn("rwis") as conn:
        df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Sorry, no results found for query!"]
    if include_latlon:
        myvars.insert(2, "longitude")
        myvars.insert(3, "latitude")

        def get_lat(station):
            """hack"""
            return nt.sts[station]["lat"]

        def get_lon(station):
            """hack"""
            return nt.sts[station]["lon"]

        df["latitude"] = [get_lat(x) for x in df["station"]]
        df["longitude"] = [get_lon(x) for x in df["station"]]

    sio = StringIO()
    if what in ["txt", "download"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=rwis.txt"),
        ]
        start_response("200 OK", headers)
        df.to_csv(sio, index=False, sep=delimiter, columns=myvars)
        return [sio.getvalue().encode("ascii")]
    if what == "html":
        start_response("200 OK", [("Content-type", "text/html")])
        df.to_html(sio, columns=myvars)
        return [sio.getvalue().encode("ascii")]
    if what == "excel":
        if len(df.index) >= 1048576:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"Dataset too large for excel format."]
        bio = BytesIO()
        with pd.ExcelWriter(bio) as writer:
            df.to_excel(writer, sheet_name="Data", index=False, columns=myvars)

        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=rwis.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]
    start_response("200 OK", [("Content-type", "text/plain")])
    df.to_csv(sio, sep=delimiter, columns=df.columns.intersection(myvars))
    return [sio.getvalue().encode("ascii")]
