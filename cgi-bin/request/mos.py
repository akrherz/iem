"""Download MOS data."""
from io import StringIO, BytesIO

import pandas as pd
from paste.request import parse_formvars
from sqlalchemy import text
from pyiem.util import get_sqlalchemy_conn, utc, LOG

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_data(sts, ets, station, model, fmt):
    """Go fetch data please"""
    model2 = model
    if model == "NAM":
        model2 = "ETA"
    if model == "GFS":
        model2 = "AVN"
    with get_sqlalchemy_conn("mos") as conn:
        df = pd.read_sql(
            text(
                """
            select
            runtime at time zone 'UTC' as utc_runtime,
            ftime at time zone 'UTC' as utc_ftime,
            *, t06_1 ||'/'||t06_2 as t06,
            t12_1 ||'/'|| t12_2 as t12  from alldata WHERE station = :station
            and runtime >= :sts and runtime <= :ets and
            (model = :model1 or model = :model2)
            ORDER by runtime,ftime ASC"""
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "model1": model,
                "model2": model2,
                "station": station,
            },
        )
    df = df.drop(columns=["runtime", "ftime"]).rename(
        columns={"utc_runtime": "runtime", "utc_ftime": "ftime"}
    )
    if not df.empty:
        df = df.dropna(axis=1, how="all")
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        # pylint: disable=abstract-class-instantiated
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, "Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


def parse_dates(form):
    """Nicely resolve dates please."""
    sts = utc(*[int(form[x]) for x in ["year1", "month1", "day1", "hour1"]])
    ets = utc(*[int(form[x]) for x in ["year2", "month2", "day2", "hour2"]])
    if ets < sts:
        sts, ets = ets, sts
    return sts, ets


def application(environ, start_response):
    """See how we are called"""
    form = parse_formvars(environ)
    try:
        sts, ets = parse_dates(form)
    except (ValueError, KeyError) as exp:
        LOG.info(exp)
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"Error while parsing provided dates, ensure they are valid."]

    fmt = form.get("format", "csv")
    station = form.get("station").upper()
    model = form.get("model").upper()
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [get_data(sts, ets, station, model, fmt).encode("ascii")]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=daily.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(sts, ets, station, model, fmt)]
