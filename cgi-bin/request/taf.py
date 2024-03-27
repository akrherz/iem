""".. title:: Terminal Aerodrome Forecast (TAF) Data

Documentation for /cgi-bin/request/taf.py
-----------------------------------------

This service provides access to Terminal Aerodrome Forecast (TAF) data for
specified stations and time ranges.

Example Usage
~~~~~~~~~~~~~

Request all of Des Moines TAF for the month of January 2024 in CSV format:

    https://mesonet.agron.iastate.edu/cgi-bin/request/taf.py?station=DSM&sts=2024-01-01T00:00Z&ets=2024-02-01T00:00Z&fmt=csv

"""

from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    fmt: str = Field(
        "csv",
        description="The format of the output file, either 'csv' or 'excel'",
    )
    tz: str = Field("UTC", description="The timezone to use for timestamps")
    sts: AwareDatetime = Field(
        None, description="The start timestamp for the data"
    )
    ets: AwareDatetime = Field(
        None, description="The end timestamp for the data"
    )
    station: ListOrCSVType = Field(
        ...,
        description=(
            "The station(s) to request data for, "
            "either multi params or comma separated"
        ),
    )
    year1: int = Field(None, description="The start year, if not using sts")
    month1: int = Field(None, description="The start month, if not using sts")
    day1: int = Field(None, description="The start day, if not using sts")
    hour1: int = Field(0, description="The start hour, if not using sts")
    minute1: int = Field(0, description="The start minute, if not using sts")
    year2: int = Field(None, description="The end year, if not using ets")
    month2: int = Field(None, description="The end month, if not using ets")
    day2: int = Field(None, description="The end day, if not using ets")
    hour2: int = Field(0, description="The end hour, if not using ets")
    minute2: int = Field(0, description="The end minute, if not using ets")


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
                "stations": ctx["station"],
                "sts": ctx["sts"],
                "ets": ctx["ets"],
            },
            parse_dates=["valid", "fx_valid", "fx_valid_end"],
        )
    # muck the timezones
    if not df.empty:
        for col in ["valid", "fx_valid", "fx_valid_end"]:
            df[col] = (
                df[col].dt.tz_localize(ctx["tz"]).dt.strftime("%Y-%m-%d %H:%M")
            )

    bio = BytesIO()
    if ctx["fmt"] == "excel":
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TAF Data", index=False)
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


@iemapp(help=__doc__, schema=MyModel, parse_times=False)
def application(environ, start_response):
    """Get stuff"""
    environ["tz"] = ZoneInfo(environ["tz"])
    if environ["sts"] is None:
        environ["sts"] = datetime(
            environ["year1"],
            environ["month1"],
            environ["day1"],
            environ["hour1"],
            environ["minute1"],
            tzinfo=environ["tz"],
        )
    if environ["ets"] is None:
        environ["ets"] = datetime(
            environ["year2"],
            environ["month2"],
            environ["day2"],
            environ["hour2"],
            environ["minute2"],
            tzinfo=environ["tz"],
        )
    environ["station"] = [rect(x) for x in environ["station"]]
    return [run(start_response, environ)]
