"""
Return a simple CSV of stuart smith data

Levelogger Reading (ft)
Barologger Reading
Temp (C)
Barologger Air Temp (C)
Conductivity (micro-S)
7.20473    ch1_data_p
2.68857     ch2_data_p
21.1       ch1_data_t
18.19    ch2_data_t
48       ch1_data_c
"""

from io import BytesIO

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

LOOKUP = {
    9100104: "SSP #6",
    9100135: "SSP #8",
    9100131: "SSP #1",
    9100156: "SSP #7",
}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    excel: bool = Field(description="Return Excel File", default=False)
    opt: str = Field(description="bubbler or gage", default="gage")
    station: ListOrCSVType = Field(
        default=[], description="Station ID to query"
    )
    sts: AwareDatetime = Field(description="Start Time", default=None)
    ets: AwareDatetime = Field(description="End Time", default=None)
    year1: int = Field(
        description="Start year, when sts is not set.", default=None
    )
    month1: int = Field(
        description="Start month, when sts is not set.", default=None
    )
    day1: int = Field(
        description="Start day, when sts is not set.", default=None
    )
    year2: int = Field(
        description="End year, when ets is not set.", default=None
    )
    month2: int = Field(
        description="End month, when ets is not set.", default=None
    )
    day2: int = Field(
        description="End day, when ets is not set.", default=None
    )


def gage_run(sts, ets, stations, excel, start_response):
    """run()"""
    if not stations:
        stations = list(LOOKUP.keys())

    sql = text(
        """select date(valid) as date, to_char(valid, 'HH24:MI:SS') as time,
    site_serial, ch1_data_p, ch2_data_p,
    ch1_data_t, ch2_data_t, ch1_data_c
    from ss_logger_data WHERE valid between :sts and :ets and
    site_serial = ANY(:stations) ORDER by valid ASC"""
    )
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(
            sql, conn, params={"sts": sts, "ets": ets, "stations": stations}
        )
    eheaders = [
        "date",
        "time",
        "site_serial",
        "Levelogger Reading (ft)",
        "Barologger Reading",
        "Water Temp (C)",
        "Barologger Air Temp (C)",
        "Conductivity (micro-S)",
    ]

    if excel:
        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=stuartsmith.xlsx"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, header=eheaders, index=False, engine="openpyxl")
        return bio.getvalue()
    start_response("200 OK", [("Content-type", "text/plain")])
    return df.to_csv(None, index=False).encode("ascii")


def bubbler_run(sts, ets, excel, start_response):
    """run()"""
    sql = text(
        """
    WITH one as (SELECT valid, value from ss_bubbler WHERE
    valid between :sts and :ets and field = 'Batt Voltage'),
    two as (SELECT valid, value from ss_bubbler WHERE
    valid between :sts and :ets and field = 'STAGE'),
    three as (SELECT valid, value from ss_bubbler WHERE
    valid between :sts and :ets and field = 'Water Temp')

    SELECT date(coalesce(one.valid, two.valid, three.valid)) as date,
    to_char(coalesce(one.valid, two.valid, three.valid), 'HH24:MI:SS') as time,
    one.value as "batt voltage",
    two.value as "stage",
    three.value as "water temp"
    from one FULL OUTER JOIN two on (one.valid = two.valid)
        FULL OUTER JOIN three on (coalesce(two.valid,one.valid) = three.valid)
    ORDER by date ASC, time ASC
    """
    )
    with get_sqlalchemy_conn("other") as conn:
        df = pd.read_sql(sql, conn, params={"sts": sts, "ets": ets})
    if excel:
        headers = [
            ("Content-type", "application/vnd.ms-excel"),
            ("Content-disposition", "attachment; Filename=stuartsmith.xls"),
        ]
        start_response("200 OK", headers)
        bio = BytesIO()
        df.to_excel(bio, index=False)
        return bio.getvalue()
    start_response("200 OK", [("Content-type", "text/plain")])
    return df.to_csv(None, index=False).encode("ascii")


@iemapp(default_tz="America/Chicago", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go Main Go"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("GET start time parameters missing")
    opt = environ["opt"]

    stations = environ["station"]
    if opt == "bubbler":
        return [
            bubbler_run(
                environ["sts"],
                environ["ets"],
                environ["excel"],
                start_response,
            )
        ]
    return [
        gage_run(
            environ["sts"],
            environ["ets"],
            stations,
            environ["excel"],
            start_response,
        )
    ]
