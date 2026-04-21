""".. title:: Download PurpleAir Data

Example Requests
----------------

Provide data for 10 August 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/purpleair.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z

and in Excel format this time

https://mesonet.agron.iastate.edu/cgi-bin/request/purpleair.py\
?sts=2024-08-10T00:00Z&ets=2024-08-11T00:00Z&excel=1

"""

from datetime import datetime
from io import BytesIO
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, iemapp

from iemweb.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    excel: Annotated[
        bool, Field(description="Return Excel file instead of CSV")
    ] = False
    sts: Annotated[
        datetime | None,
        Field(description="Start time of data to query, in ISO format"),
    ] = None
    ets: Annotated[
        datetime | None,
        Field(description="End time of data to query, in ISO format"),
    ] = None
    year1: YEAR_FIELD_OPTIONAL = None
    year2: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    hour2: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    minute2: MINUTE_FIELD = 0


def run(environ, start_response):
    """run()"""
    sql = sql_helper(
        """
    select * from purpleair where valid >= :sts and valid < :ets
    ORDER by valid asc
    """
    )
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            sql, conn, params={"sts": environ["sts"], "ets": environ["ets"]}
        )
    if environ["excel"]:
        df["valid"] = df["valid"].dt.strftime("%Y-%m-%d %H:%M")
        start_response(
            "200 OK",
            [
                ("Content-type", EXL),
                ("Content-Disposition", "attachment; filename=purpleair.xlsx"),
            ],
        )
        bio = BytesIO()
        df.to_excel(bio, index=False, engine="openpyxl")
        return bio.getvalue()
    start_response(
        "200 OK",
        [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=purpleair.csv"),
        ],
    )
    return df.to_csv(None, index=False).encode("ascii")


@iemapp(schema=Schema, default_tz="America/Chicago", help=__doc__)
def application(environ, start_response):
    """Go Main Go"""
    if "sts" not in environ:
        raise IncompleteWebRequest("GET start time parameters missing")

    return [run(environ, start_response)]
