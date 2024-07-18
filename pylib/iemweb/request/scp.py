""".. title:: Satellite Cloud Product (SCP) Request

Documentation for /cgi-bin/request/scp.py
--------------------------------------------

This script is used to request Satellite Cloud Product (SCP) data from the
IEM's ASOS database.

Examples:
---------

Download all 2023 data for KBUR

  https://mesonet.agron.iastate.edu/cgi-bin/request/scp.py?station=KBUR&sts=2023-01-01T00:00Z&ets=2024-01-01T00:00Z

"""

from io import StringIO

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text


class Schema(CGIModel):
    """Our schema for this request"""

    ets: AwareDatetime = Field(
        None,
        description=(
            "End timestamp with timezone included to request data for."
        ),
    )
    station: ListOrCSVType = Field(
        None,
        description=(
            "Four or Five character station identifier(s) to request data for."
        ),
    )
    sts: AwareDatetime = Field(
        None,
        description=(
            "Start timestamp with timezone included to request data for."
        ),
    )
    year1: int = Field(
        None,
        description=(
            "Year to request data for, this is an alternative to sts/ets."
        ),
    )
    year2: int = Field(
        None,
        description=(
            "Year to request data for, this is an alternative to sts/ets."
        ),
    )
    month1: int = Field(
        None,
        description=(
            "Month to request data for, this is an alternative to sts/ets."
        ),
    )
    month2: int = Field(
        None,
        description=(
            "Month to request data for, this is an alternative to sts/ets."
        ),
    )
    day1: int = Field(
        None,
        description=(
            "Day to request data for, this is an alternative to sts/ets."
        ),
    )
    day2: int = Field(
        None,
        description=(
            "Day to request data for, this is an alternative to sts/ets."
        ),
    )
    hour1: int = Field(0, description="Hour to request data for.")
    hour2: int = Field(0, description="Hour to request data for.")
    minute1: int = Field(0, description="Minute to request data for.")
    minute2: int = Field(0, description="Minute to request data for.")


@iemapp(schema=Schema, help=__doc__)
def application(environ, start_response):
    """Do Something"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Both start and end time must be provided!")
    start_response("200 OK", [("Content-type", "text/plain")])
    slimiter = ""
    params = {
        "sts": environ["sts"],
        "ets": environ["ets"],
        "station": environ["station"],
    }
    if environ["station"]:
        slimiter = "station = ANY(:station)"
    sio = StringIO()
    sio.write("station,utc_valid,mid,high,cldtop1,cldtop2,eca,source\n")
    with get_sqlalchemy_conn("asos") as conn:
        res = conn.execute(
            text(f"""
            SELECT station, valid at time zone 'UTC' as utc_valid, mid, high,
            cldtop1, cldtop2, eca, source from scp_alldata
            WHERE valid >= :sts and valid < :ets and {slimiter}
            ORDER by valid ASC
        """),
            params,
        )
        for row in res:
            sio.write(
                ("%s,%s,%s,%s,%s,%s,%s,%s\n")
                % (
                    row[0],
                    row[1].strftime("%Y-%m-%d %H:%M:%S"),
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                )
            )
    return [sio.getvalue().encode("ascii", "ignore")]
