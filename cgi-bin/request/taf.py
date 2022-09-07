"""TAF."""
# pylint: disable=abstract-class-instantiated
import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from paste.request import parse_formvars
from sqlalchemy import text
from pyiem.util import get_sqlalchemy_conn

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def run(start_response, ctx):
    """Get data!"""
    with get_sqlalchemy_conn("asos") as dbconn:
        df = pd.read_sql(
            text(
                """
            select t.station, t.valid at time zone 'UTC' as valid,
            f.valid at time zone 'UTC' as fx_valid, raw, is_tempo,
            end_valid at time zone 'UTC' as fx_valid_end,
            sknt, drct, gust, visibility,
            presentwx, skyc, skyl, ws_level, ws_drct, ws_sknt, product_id
            from taf t JOIN taf_forecast f on (t.id = f.taf_id)
            WHERE t.station in :stations and f.valid >= :sts
            and f.valid < :ets order by t.valid
            """
            ),
            dbconn,
            params={
                "stations": tuple(ctx["stations"]),
                "sts": ctx["sts"],
                "ets": ctx["ets"],
            },
        )
    # muck the timezones
    for col in ["valid", "fx_valid", "fx_valid_end"]:
        try:
            df[col] = (
                df[col].dt.tz_localize(ctx["tz"]).dt.strftime("%Y-%m-%d %H:%M")
            )
        except Exception:
            pass

    bio = BytesIO()
    if ctx["fmt"] == "excel":
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, "TAF Data", index=False)
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment;Filename=taf.xlsx"),
        ]
    else:
        df.to_csv(bio, index=False)
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment;Filename=taf.csv"),
        ]
    start_response("200 OK", headers)
    return bio.getvalue()


def rect(station):
    """Cleanup."""
    station = station.upper()
    if len(station) == 3:
        return f"K{station}"
    return station


def application(environ, start_response):
    """Get stuff"""
    form = parse_formvars(environ)
    ctx = {}
    ctx["fmt"] = form.get("fmt")
    ctx["tz"] = ZoneInfo(form.get("tz", "UTC"))
    ctx["stations"] = [rect(x) for x in form.getall("station")]
    if not ctx["stations"]:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"Must specify at least one station!"]
    year1 = int(form.get("year1"))
    year2 = int(form.get("year2"))
    month1 = int(form.get("month1"))
    month2 = int(form.get("month2"))
    day1 = int(form.get("day1"))
    day2 = int(form.get("day2"))

    ctx["sts"] = datetime.datetime(year1, month1, day1, tzinfo=ctx["tz"])
    ctx["ets"] = datetime.datetime(year2, month2, day2, tzinfo=ctx["tz"])

    return [run(start_response, ctx)]
