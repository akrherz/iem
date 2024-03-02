"""
Download Interface for HADS data
"""

# pylint: disable=abstract-class-instantiated
from datetime import timedelta
from io import BytesIO, StringIO

import pandas as pd
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.util import get_sqlalchemy_conn
from pyiem.webutil import ensure_list, iemapp
from sqlalchemy import text

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def threshold_search(table, threshold, thresholdvar):
    """Do the threshold searching magic"""
    cols = list(table.columns.values)
    searchfor = f"HGI{thresholdvar.upper()}"
    cols5 = [s[:5] for s in cols]
    mycol = cols[cols5.index(searchfor)]
    above = False
    maxrunning = -99
    maxvalid = None
    res = []
    for (station, valid), row in table.iterrows():
        val = row[mycol]
        if val > threshold and not above:
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="START",
                    value=val,
                    varname=mycol,
                )
            )
            above = True
        if val > threshold and above:
            if val > maxrunning:
                maxrunning = val
                maxvalid = valid
        if val < threshold and above:
            res.append(
                dict(
                    station=station,
                    utc_valid=maxvalid,
                    event="MAX",
                    value=maxrunning,
                    varname=mycol,
                )
            )
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="END",
                    value=val,
                    varname=mycol,
                )
            )
            above = False
            maxrunning = -99
            maxvalid = None

    return pd.DataFrame(res)


@iemapp(default_tz="UTC")
def application(environ, start_response):
    """Go do something"""
    network = environ.get("network")
    delimiter = DELIMITERS.get(environ.get("delim", "comma"))
    what = environ.get("what", "dl")
    threshold = environ.get("threshold", -99)
    if threshold is not None and threshold != "":
        threshold = float(threshold)
    thresholdvar = environ.get("threshold-var", "RG")
    stations = ensure_list(environ, "stations")
    if "_ALL" in stations and network is not None:
        stations = list(NetworkTable(network[:10]).sts.keys())
        if (environ["ets"] - environ["sts"]) > timedelta(hours=24):
            environ["ets"] = environ["sts"] + timedelta(hours=24)
    if not stations:
        raise IncompleteWebRequest("Error, no stations specified!")

    sql = text(
        f"""
        SELECT station, valid at time zone 'UTC' as utc_valid, key, value
        from raw{environ['sts'].year} WHERE station = ANY(:ids) and
        valid BETWEEN :sts and :ets and value > -999
        ORDER by valid ASC
        """
    )
    params = {"ids": stations, "sts": environ["sts"], "ets": environ["ets"]}

    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Error, no results found for query!"]
    table = df.pivot_table(
        values="value", columns=["key"], index=["station", "utc_valid"]
    )
    if threshold != "" and threshold >= 0:
        if "XXXXXXX" not in stations:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"Can not do threshold search for more than one station"]
        table = threshold_search(table, threshold, thresholdvar)

    sio = StringIO()
    if what == "txt":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=hads.txt"),
        ]
        start_response("200 OK", headers)
        table.to_csv(sio, sep=delimiter)
        return [sio.getvalue().encode("ascii")]
    if what == "html":
        headers = [("Content-type", "text/html")]
        start_response("200 OK", headers)
        table.to_html(sio)
        return [sio.getvalue().encode("ascii")]
    if what == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            table.to_excel(writer, sheet_name="Data", index=True)

        headers = [
            ("Content-type", EXL),
            ("Content-Disposition", "attachment; filename=hads.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]
    start_response("200 OK", [("Content-type", "text/plain")])
    table.to_csv(sio, sep=delimiter)
    return [sio.getvalue().encode("ascii")]
