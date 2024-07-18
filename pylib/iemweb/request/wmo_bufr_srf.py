""".. title:: WMO BUFR Surface Data

Documentation for /cgi-bin/request/wmo_bufr_srf.py
--------------------------------------------------

This application provides access to the IEM processed archives of stations
reporting via the WMO BUFR Surface.

"""

from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class MyModel(CGIModel):
    """Our model"""

    format: str = Field(
        "csv",
        description="The format of the data response. csv, json, or excel",
        pattern=r"^(csv|json|excel)$",
    )
    ets: AwareDatetime = Field(
        None,
        description="The end time for the data request",
    )
    stations: ListOrCSVType = Field(..., description="The station identifiers")
    sts: AwareDatetime = Field(
        None,
        description="The start time for the data request",
    )
    year1: int = Field(
        None,
        description="The start year for the data request, when sts is not set",
    )
    month1: int = Field(
        None,
        description=(
            "The start month for the data request, when sts is not set"
        ),
    )
    day1: int = Field(
        None,
        description="The start day for the data request, when sts is not set",
    )
    hour1: int = Field(
        None,
        description="The start hour for the data request, when sts is not set",
    )
    year2: int = Field(
        None,
        description="The end year for the data request, when ets is not set",
    )
    month2: int = Field(
        None,
        description="The end month for the data request, when ets is not set",
    )
    day2: int = Field(
        None,
        description="The end day for the data request, when ets is not set",
    )
    hour2: int = Field(
        None,
        description="The end hour for the data request, when ets is not set",
    )


def get_data(sts, ets, stations, fmt):
    """Go fetch data please"""
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            text(
                """
            select
            valid at time zone 'UTC' as utc_valid, * from alldata
            WHERE station = ANY(:stations)
            and valid >= :sts and valid <= :ets
            ORDER by valid, station ASC"""
            ),
            conn,
            params={
                "sts": sts,
                "ets": ets,
                "stations": stations,
            },
        )
    df = df.drop(columns=["valid"])
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        # pylint: disable=abstract-class-instantiated
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=MyModel, default_tz="UTC")
def application(environ, start_response):
    """See how we are called"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing sts and/or ets")
    stations = environ["stations"]
    fmt = environ["format"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return get_data(environ["sts"], environ["ets"], stations, fmt)
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=mos.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(environ["sts"], environ["ets"], stations, fmt)]
