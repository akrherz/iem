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

from pydantic import Field
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp


class Schema(CGIModel):
    """See how we are called."""

    delim: str = Field(
        "comma",
        description=(
            "The delimiter to use in the output file.  "
            "Options: comma, tab, space"
        ),
        pattern="^(comma|tab|space)$",
    )
    network: str = Field(
        ..., description="The network to use for station lookups."
    )
    stations: ListOrCSVType = Field(
        ...,
        description=(
            "List of stations to include in the output. Legacy variable name."
        ),
    )
    what: str = Field("view", description="The type of output to generate.")
    sts: date = Field(
        None,
        description="The starting date for the data request.",
    )
    ets: date = Field(
        None,
        description="The ending date for the data request.",
    )
    year1: int = Field(
        None,
        description="The starting year for the data request.",
    )
    month1: int = Field(
        None,
        description="The starting month for the data request.",
    )
    day1: int = Field(
        None,
        description="The starting day for the data request.",
    )
    year2: int = Field(
        None,
        description="The ending year for the data request.",
    )
    month2: int = Field(
        None,
        description="The ending month for the data request.",
    )
    day2: int = Field(
        None,
        description="The ending day for the data request.",
    )


def get_cgi_stations(environ):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = environ["stations"]
    if "_ALL" in reqlist:
        nt = NetworkTable(environ["network"], only_online=False)
        return list(nt.sts.keys())

    return reqlist


@with_sqlalchemy_conn("iem")
def do_simple(ctx, conn=None):
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

    start_response("200 OK", headers)
    res = do_simple(environ)
    return [res]
