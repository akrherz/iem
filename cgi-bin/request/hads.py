"""
Download Interface for HADS data
"""
# pylint: disable=abstract-class-instantiated
from io import StringIO, BytesIO

import pandas as pd
from pandas.io.sql import read_sql
from paste.request import parse_formvars
from pyiem.util import get_sqlalchemy_conn, utc
from sqlalchemy import text

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_time(form):
    """Get timestamps"""
    y1 = int(form.get("year"))
    m1 = int(form.get("month1"))
    m2 = int(form.get("month2"))
    d1 = int(form.get("day1"))
    d2 = int(form.get("day2"))
    h1 = int(form.get("hour1", 0))
    h2 = int(form.get("hour2", 0))
    mi1 = int(form.get("minute1", 0))
    mi2 = int(form.get("minute2", 0))
    sts = utc(y1, m1, d1, h1, mi1)
    ets = utc(y1, m2, d2, h2, mi2)
    return sts, ets


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


def application(environ, start_response):
    """Go do something"""
    form = parse_formvars(environ)
    # network = form.get('network')
    delimiter = DELIMITERS.get(form.get("delim", "comma"))
    what = form.get("what", "dl")
    threshold = form.get("threshold", -99)
    if threshold is not None and threshold != "":
        threshold = float(threshold)
    thresholdvar = form.get("threshold-var", "RG")
    sts, ets = get_time(form)
    stations = form.getall("stations")
    if not stations:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Error, no stations specified for the query!"]

    sql = text(
        f"""
        SELECT station, valid at time zone 'UTC' as utc_valid, key, value
        from raw{sts.year} WHERE station in :ids and
        valid BETWEEN :sts and :ets and value > -999
        """
    )
    params = {"ids": tuple(stations), "sts": sts, "ets": ets}

    with get_sqlalchemy_conn("hads") as conn:
        df = read_sql(sql, conn, params=params)
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
            table.to_excel(writer, "Data", index=True)

        headers = [
            ("Content-type", EXL),
            ("Content-Disposition", "attachment; filename=hads.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]
    start_response("200 OK", [("Content-type", "text/plain")])
    table.to_csv(sio, sep=delimiter)
    return [sio.getvalue().encode("ascii")]
