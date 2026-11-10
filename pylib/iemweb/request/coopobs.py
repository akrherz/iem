""".. title:: NWS COOP Observations Download

Return to `API Services </api/#cgi>`_.  This service is the backend for the
`COOP Obs Download </request/coop/obs-fe.phtml>`_ frontend.

Documentation for /cgi-bin/request/coopobs.py
---------------------------------------------

This service emits the raw COOP observations without much IEM processing. If
you request `_ALL` stations for a state or more than 10 stations, you are
limited to one calendar year of data.

Changelog
---------

- 2025-02-22: Initial implementation

Example Usage
-------------

Fetch the COOP observations for Iowa on 22 October 2024 in CSV format:

https://mesonet.agron.iastate.edu/cgi-bin/request/coopobs.py?\
network=IA_COOP&stations=_ALL&sts=2024-10-22\
&ets=2024-10-22&what=download&delim=comma

Same request, but view the data instead of downloading it:

https://mesonet.agron.iastate.edu/cgi-bin/request/coopobs.py?\
network=IA_COOP&stations=_ALL&sts=2024-10-22\
&ets=2024-10-22&what=view&delim=comma

Download the COOP observations for Ames, IA on 22 October 2024 in CSV format:

https://mesonet.agron.iastate.edu/cgi-bin/request/coopobs.py?\
network=IA_COOP&stations=AESI4&sts=2024-10-22&ets=2024-10-22&what=download\
&delim=comma

"""

from datetime import date
from io import StringIO
from typing import Annotated

from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    MONTH_FIELD_OPTIONAL,
    NETWORK_FIELD,
    STATION_LIST_FIELD,
)
from pyiem.webutil import CGIModel, iemapp


class Schema(CGIModel):
    """See how we are called."""

    delim: Annotated[
        str,
        Field(
            description=(
                "The delimiter to use in the output file.  "
                "Options: comma, tab, space"
            ),
            pattern="^(comma|tab|space)$",
        ),
    ] = "comma"
    network: NETWORK_FIELD
    stations: STATION_LIST_FIELD
    what: str = Field("view", description="The type of output to generate.")
    sts: Annotated[
        date | None,
        Field(
            description="The starting date for the data request.",
        ),
    ] = None
    ets: Annotated[
        date | None,
        Field(
            description="The ending date for the data request.",
        ),
    ] = None
    year1: Annotated[
        int | None,
        Field(
            description="The starting year for the data request.",
        ),
    ] = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    year2: Annotated[
        int | None,
        Field(
            description="The ending year for the data request.",
        ),
    ] = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None


def get_cgi_stations(environ):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = environ["stations"]
    if "_ALL" in reqlist:
        nt = NetworkTable(environ["network"], only_online=False)
        return list(nt.sts.keys())

    return reqlist


def do_simple(ctx, conn):
    """Generate Simple output"""
    res = conn.execute(
        sql_helper(
            """
 SELECT s.*,t.id, day,
 coalesce(to_char(coop_valid at time zone t.tzname, 'HH PM'), '') as cv
 from summary s JOIN stations t on (t.iemid = s.iemid)
 WHERE day >= :sts and day <= :ets
 and id = ANY(:stations) and network = :network ORDER by s.day ASC"""
        ),
        {
            "stations": ctx["stations"],
            "sts": ctx["sts"],
            "ets": ctx["ets"],
            "network": ctx["network"],
        },
    )
    p = {"comma": ",", "tab": "\t", "space": " "}
    d = p[ctx["delim"]]
    cols = [
        "nwsli",
        "date",
        "time",
        "high_F",
        "low_F",
        "precip",
        "snow_inch",
        "snowd_inch",
    ]
    with StringIO() as sio:
        sio.write(d.join(cols) + "\n")
        for row in res.mappings():
            sio.write(row["id"] + d)
            sio.write(row["day"].strftime("%Y-%m-%d") + d)
            sio.write(row["cv"] + d)
            sio.write(f"{row['max_tmpf']}{d}")
            sio.write(f"{row['min_tmpf']}{d}")
            sio.write(f"{row['pday']}{d}")
            sio.write(f"{row['snow']}{d}")
            sio.write(f"{row['snowd']}\n")
        return sio.getvalue().replace("None", "").encode("ascii")


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """go main go"""
    if environ["ets"] is None or environ["sts"] is None:
        raise IncompleteWebRequest("Missing start or end date")
    environ["stations"] = get_cgi_stations(environ)
    if (
        len(environ["stations"]) > 10
        and (environ["ets"] - environ["sts"]).days > 366
    ):
        raise IncompleteWebRequest(
            "Limited to less than 1 year when requesting 10+ stations."
        )

    headers = [("Content-type", "text/plain")]
    if environ["what"] == "download":
        headers.append(
            ("Content-Disposition", "attachment; filename=coop.txt")
        )

    with get_sqlalchemy_conn("iem") as conn:
        res = do_simple(environ, conn)
    start_response("200 OK", headers)
    return res
