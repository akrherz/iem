""".. title:: Terminal Aerodrome Forecast (TAF) Data

Return to `API Services </api/#cgi>`_ or `TAF Request </request/taf.php>`_.

Documentation for /cgi-bin/request/taf.py
-----------------------------------------

This service provides access to Terminal Aerodrome Forecast (TAF) data for
specified stations and time ranges. The time range limits the TAF issuance
timestamps, not the forecast valid times.

Example Usage
~~~~~~~~~~~~~

Request all of Des Moines TAF for the month of August 2024 in CSV format and
then excel format:

https://mesonet.agron.iastate.edu/cgi-bin/request/taf.py\
?station=DSM&sts=2024-08-01T00:00Z&ets=2024-09-01T00:00Z&fmt=csv

https://mesonet.agron.iastate.edu/cgi-bin/request/taf.py\
?station=DSM&sts=2024-08-01T00:00Z&ets=2024-09-01T00:00Z&fmt=excel

Request the past 240 hours of TAF data for Chicago O'Hare in Excel format:

https://mesonet.agron.iastate.edu/cgi-bin/request/taf.py\
?station=ORD&hours=240&fmt=excel

Request the last TAF issuance for Des Moines valid prior to 00 UTC on 21 August
2024 in CSV format:

https://mesonet.agron.iastate.edu/cgi-bin/request/taf.py\
?station=DSM&ets=2024-08-21T00:00Z&sts=2024-08-19T00:00Z&fmt=csv&last=1

"""

from datetime import timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    hours: int = Field(
        None,
        description=(
            "Request data for the time period from now until this many hours "
            "in the past. Overrides any sts or ets values."
        ),
        le=2400,
        gt=0,
    )
    fmt: str = Field(
        "csv",
        description="The format of the output file, either 'csv' or 'excel'",
    )
    last: bool = Field(
        default=False,
        description=(
            "If True, the last TAF issuance for the station(s) is returned, "
            "which is defined as last issuance prior to or equal to the end "
            "timestamp."
        ),
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


def run(start_response, environ):
    """Get data!"""
    with get_sqlalchemy_conn("asos") as dbconn:
        df = pd.read_sql(
            sql_helper(
                """
            select t.station, t.valid at time zone 'UTC' as valid,
            f.valid at time zone 'UTC' as fx_valid, raw, is_tempo,
            end_valid at time zone 'UTC' as fx_valid_end,
            sknt, drct, gust, visibility,
            presentwx, skyc, skyl, ws_level, ws_drct, ws_sknt, product_id,
            rank() OVER (PARTITION by t.station ORDER by t.valid DESC)
            from taf t JOIN taf_forecast f on (t.id = f.taf_id)
            WHERE t.station = ANY(:stations) and t.valid >= :sts
            and t.valid < :ets order by t.valid asc, f.valid asc
            """
            ),
            dbconn,
            params={
                "stations": environ["station"],
                "sts": environ["sts"],
                "ets": environ["ets"],
            },
            parse_dates=["valid", "fx_valid", "fx_valid_end"],
        )
    # muck the timezones
    if not df.empty:
        tzinfo = ZoneInfo(environ["tz"])
        for col in ["valid", "fx_valid", "fx_valid_end"]:
            df[col] = (
                df[col].dt.tz_localize(tzinfo).dt.strftime("%Y-%m-%d %H:%M")
            )
    if environ["last"]:
        df = df[df["rank"] == 1]
    df = df.drop(columns=["rank"])

    bio = BytesIO()
    if environ["fmt"] == "excel":
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
    return station if len(station) == 4 else f"K{station}"


@iemapp(help=__doc__, schema=MyModel)
def application(environ, start_response):
    """Get stuff"""
    if environ["hours"] is not None:
        environ["ets"] = utc()
        environ["sts"] = environ["ets"] - timedelta(hours=environ["hours"])
    environ["station"] = [rect(x.upper()) for x in environ["station"]]
    return [run(start_response, environ)]
