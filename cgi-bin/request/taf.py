"""TAF."""
# pylint: disable=abstract-class-instantiated
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from pyiem.util import LOG, get_sqlalchemy_conn
from pyiem.webutil import iemapp
from sqlalchemy import text

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
            WHERE t.station = ANY(:stations) and f.valid >= :sts
            and f.valid < :ets order by t.valid
            """
            ),
            dbconn,
            params={
                "stations": ctx["stations"],
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
        except Exception as exp:
            LOG.debug(exp)

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


@iemapp()
def application(environ, start_response):
    """Get stuff"""
    ctx = {}
    ctx["fmt"] = environ.get("fmt")
    ctx["tz"] = ZoneInfo(environ.get("tz", "UTC"))
    ctx["sts"] = environ["sts"]
    ctx["ets"] = environ["ets"]
    stations = environ.get("station", [])
    if not isinstance(stations, list):
        stations = [stations]
    ctx["stations"] = [rect(x) for x in stations]
    if not ctx["stations"]:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        return [b"Must specify at least one station!"]
    return [run(start_response, ctx)]
