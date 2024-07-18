""".. title:: Temperature and Wind Aloft Data Service

Documentation for /cgi-bin/request/tempwind_aloft.py
----------------------------------------------------

This service emits processed data from a temperature and winds aloft product.

Example Usage
~~~~~~~~~~~~~

Request all data for `KDSM` for 2023.

https://mesonet.agron.iastate.edu/cgi-bin/request/tempwind_aloft.py?station=KDSM&sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z

"""

from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    ets: AwareDatetime = Field(
        None,
        description="The end time of the data request",
    )
    format: str = Field(
        "csv",
        description="The format of the output (csv json or excel)",
        pattern="^(csv|json|excel)$",
    )
    na: str = Field(
        "M",
        description="The value to use for missing data",
        pattern="^(M|None|blank)$",
    )
    sts: AwareDatetime = Field(
        None,
        description="The start time of the data request",
    )
    station: ListOrCSVType = Field(
        ...,
        description="The station identifier(s) to request data for",
    )
    tz: str = Field(
        "UTC",
        description=(
            "The timezone to use for timestamps in request and response, it "
            "should be something recognized by the pytz library."
        ),
    )
    year1: int = Field(
        None,
        description="The year for the start time, if sts is not provided",
    )
    year2: int = Field(
        None,
        description="The year for the end time, if ets is not provided",
    )
    month1: int = Field(
        None,
        description="The month for the start time, if sts is not provided",
    )
    month2: int = Field(
        None,
        description="The month for the end time, if ets is not provided",
    )
    day1: int = Field(
        None,
        description="The day for the start time, if sts is not provided",
    )
    day2: int = Field(
        None,
        description="The day for the end time, if ets is not provided",
    )


def get_data(stations, sts, ets, tz, na, fmt):
    """Go fetch data please"""
    with get_sqlalchemy_conn("asos") as conn:
        df = pd.read_sql(
            text(
                """
            SELECT *,
            to_char(obtime at time zone :tz, 'YYYY/MM/DD HH24:MI')
                as obtime2,
            to_char(ftime at time zone :tz, 'YYYY/MM/DD HH24:MI')
                as ftime2
            from alldata_tempwind_aloft WHERE ftime >= :sts and
            ftime <= :ets and station = ANY(:stations) ORDER by obtime, ftime
            """
            ),
            conn,
            params={"sts": sts, "ets": ets, "stations": stations, "tz": tz},
        )
    df = df.drop(columns=["obtime", "ftime"]).rename(
        columns={"obtime2": "obtime", "ftime2": "ftime"}
    )
    cols = df.columns.values.tolist()
    cols.remove("ftime")
    cols.remove("obtime")
    cols.insert(1, "obtime")
    cols.insert(2, "ftime")
    df = df[cols].dropna(axis=1, how="all")
    if na != "blank":
        df = df.fillna(na)
    if fmt == "json":
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """See how we are called"""

    fmt = environ["format"]
    tz = environ["tz"]
    stations = environ["station"]
    na = environ["na"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            get_data(
                stations, environ["sts"], environ["ets"], tz, na, fmt
            ).encode("ascii")
        ]
    lll = "stations" if len(stations) > 1 else stations[0]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", f"attachment; Filename={lll}.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(stations, environ["sts"], environ["ets"], tz, na, fmt)]
