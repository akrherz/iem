"""Process talltowers data request."""
import datetime
from io import BytesIO, StringIO
from zoneinfo import ZoneInfo

import pandas as pd
from paste.request import parse_formvars
from pyiem.util import get_dbconn, get_sqlalchemy_conn

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

TOWERIDS = {0: "ETTI4", 1: "MCAI4"}


def get_stations(form):
    """Figure out the requested station"""
    stations = form.getall("station")
    towers = []
    for tid, nwsli in TOWERIDS.items():
        if nwsli in stations:
            towers.append(tid)

    return towers


def get_time_bounds(form, tzinfo):
    """Figure out the exact time bounds desired"""
    y1 = int(form.get("year1"))
    y2 = int(form.get("year2"))
    m1 = int(form.get("month1"))
    m2 = int(form.get("month2"))
    d1 = int(form.get("day1"))
    d2 = int(form.get("day2"))
    h1 = int(form.get("hour1"))
    h2 = int(form.get("hour2"))
    sts = datetime.datetime(y1, m1, d1, h1, tzinfo=tzinfo)
    ets = datetime.datetime(y2, m2, d2, h2, tzinfo=tzinfo)
    if ets < sts:
        sts, ets = ets, sts
    ets = min([sts + datetime.timedelta(days=32), ets])

    return sts, ets


def get_columns(cursor):
    """What have we here."""
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name   = 'data_analog'"
    )
    res = []
    for row in cursor:
        res.append(row[0])
    return res


def application(environ, start_response):
    """Go main Go"""
    pgconn = get_dbconn("talltowers", user="tt_web")
    columns = get_columns(pgconn.cursor())
    form = parse_formvars(environ)
    tzname = form.get("tz", "Etc/UTC")
    tzinfo = ZoneInfo(tzname)

    stations = get_stations(form)
    if not stations:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"No stations provided"]
    sts, ets = get_time_bounds(form, tzinfo)
    fmt = form.get("format")
    # Build out our variable list
    tokens = []
    for z in form.getall("z"):
        for v in form.getall("var"):
            v1 = v
            v2 = ""
            if v.find("_") > -1:
                v1, v2 = v.split("_")
                v2 = f"_{v2}"
            colname = f"{v1}_{z}m{v2}"
            if colname not in columns:
                continue
            for agg in form.getall("agg"):
                tokens.append(f"{agg}({colname}) as {colname}_{agg}")

    tw = int(form.get("window", 1))

    sql = f"""
    SELECT tower,
    (date_trunc('hour', valid) +
    (((date_part('minute', valid)::integer / {tw}::integer) * {tw}::integer)
     || ' minutes')::interval) at time zone %s as ts,
    {','.join(tokens)} from
    data_analog where tower = ANY(%s) and valid >= %s and valid < %s
    GROUP by tower, ts ORDER by tower, ts
    """
    with get_sqlalchemy_conn("talltowers", user="tt_web") as conn:
        df = pd.read_sql(
            sql,
            conn,
            params=(tzname, stations, sts, ets),
        )
    df = df.rename(columns={"ts": "valid"})
    df["tower"] = df["tower"].replace(TOWERIDS)
    pgconn.close()
    if fmt in ["tdf", "comma"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=talltowers.txt"),
        ]
        start_response("200 OK", headers)
        sio = StringIO()
        df.to_csv(sio, sep="," if fmt == "comma" else "\t", index=False)
        return [sio.getvalue().encode("utf8")]

    # Excel
    bio = BytesIO()
    # pylint: disable=abstract-class-instantiated
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, "Data", index=False)
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=talltowers.xlsx"),
    ]
    start_response("200 OK", headers)
    return [bio.getvalue()]
