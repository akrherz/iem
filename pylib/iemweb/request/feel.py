""".. title:: ISU FEEL Data Download

Unexciting service that emits data from the ISU FEEL site.

Changelog
---------

- 2025-04-15: Initial implementation with pydantic validation.

Example Requests
----------------

Provide the data for 14 April 2025.

https://mesonet.agron.iastate.edu/cgi-bin/request/feel.py?\
year1=2025&month1=4&day1=14&year2=2025&month2=4&day2=15

"""

from datetime import datetime
from io import BytesIO
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    MONTH_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, iemapp
from sqlalchemy.engine import Connection

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    sts: Annotated[
        datetime | None,
        Field(
            description="Start Time",
        ),
    ] = None
    ets: Annotated[
        datetime | None,
        Field(
            description="End Time",
        ),
    ] = None
    year1: Annotated[
        int | None,
        Field(
            ge=2013,
            description="Start Year",
        ),
    ] = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    year2: Annotated[
        int | None,
        Field(
            ge=2013,
            description="End Year",
        ),
    ] = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None


def run(sts, ets, conn: Connection):
    """Get data!"""
    params = {"sts": sts, "ets": ets}
    sql = (
        "SELECT * from feel_data_daily where "
        "valid >= :sts and valid < :ets ORDER by valid ASC"
    )
    df = pd.read_sql(sql_helper(sql), conn, params=params)

    sql = (
        "SELECT * from feel_data_hourly where "
        "valid >= :sts and valid < :ets ORDER by valid ASC"
    )
    df2 = pd.read_sql(sql_helper(sql), conn, params=params)

    def fmt(val):
        """Lovely hack."""
        return val.strftime("%Y-%m-%d %H:%M")

    df2["valid"] = df2["valid"].apply(fmt)

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Daily Data", index=False)
        df2.to_excel(writer, sheet_name="Hourly Data", index=False)

    return bio.getvalue()


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Get stuff"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("GET parameters for start time missing")
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment;Filename=feel.xlsx"),
    ]

    with get_sqlalchemy_conn("other") as conn:
        payload = run(environ["sts"], environ["ets"], conn)
    start_response("200 OK", headers)
    return payload
