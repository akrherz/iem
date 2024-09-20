""".. title:: RWIS Download

Return to `API Services </api/#cgi>`_ and
`RWIS Download Portal </request/rwis/fe.phtml>`_

Documentation for /cgi-bin/request/rwis.py
------------------------------------------

This service emits RWIS data.

Changelog
---------

- 2024-09-19: Fix bug with no variables returned when ``vars`` is not set
- 2024-08-01: Initital documentation release and pydantic validation

Example Requests
----------------

Provide all Iowa RWIS data for 1 July 2024 in Excel format:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=_ALL&tz=America%2FChicago&what=excel&src=atmos&\
sts=2024-07-01T00:00&ets=2024-07-02T00:00

Provide all traffic data on 1 July 2024 for Iowa RWIS station RAVI4
in CSV format:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=RAVI4&tz=America%2FChicago&what=download&src=traffic&\
sts=2024-07-01T00:00&ets=2024-07-02T00:00

Provide all soil data on 1 July 2024 for Iowa RWIS stations RAKI4 in a HTML
table:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=RAKI4&tz=America%2FChicago&what=html&src=soil&\
sts=2024-07-01T00:00&ets=2024-07-02T00:00

Provide all atmospheric data on 1 July 2024 for Iowa RWIS stations RAKI4 in
a text file:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=RAKI4&tz=America%2FChicago&what=txt&src=atmos&\
sts=2024-07-01T00:00:00&ets=2024-07-02T00:00:00

Provide all atmospheric data for 31 July 2024 in UTC timezone for
Minnesota RWIS stations:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=MN_RWIS&\
stations=_ALL&tz=UTC&what=download&src=atmos&\
sts=2024-07-31T00:00&ets=2024-08-01T00:00

"""

from datetime import datetime
from io import BytesIO, StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    delim: str = Field(
        default="comma",
        description="Delimiter to use in output file",
        pattern="^(comma|space|tab)$",
    )
    gis: bool = Field(
        default=False,
        description="Include latitude and longitude columns in output",
    )
    vars: ListOrCSVType = Field(
        default=[],
        description=(
            "List of variables to include in output, if none are set, "
            "then all variables are returned for the given ``src``"
        ),
    )
    what: str = Field(
        default="dl",
        description="What to do with the data",
        pattern="^(dl|txt|html|excel|download)$",
    )
    tz: str = Field(
        default="UTC",
        description="Timezone to use for timestamps",
    )
    src: str = Field(
        default="atmos",
        description="Data source to use",
        pattern="^(atmos|soil|traffic)$",
    )
    stations: ListOrCSVType = Field(
        default=[],
        description=(
            "List of stations to include in output, `_ALL` for all stations"
        ),
    )
    network: str = Field(
        default="IA_RWIS",
        description="Network to use",
        pattern="RWIS",
    )
    sts: datetime = Field(
        default=None,
        description="Start timestamp",
    )
    ets: datetime = Field(
        default=None,
        description="End timestamp",
    )
    year1: int = Field(
        default=None,
        description="Year to start from, if sts is not set.",
    )
    month1: int = Field(
        default=None,
        description="Month to start from, if sts is not set.",
    )
    day1: int = Field(
        default=None,
        description="Day to start from, if sts is not set.",
    )
    hour1: int = Field(
        default=None,
        description="Hour to start from, if sts is not set.",
    )
    minute1: int = Field(
        default=None,
        description="Minute to start from, if sts is not set.",
    )
    year2: int = Field(
        default=None,
        description="Year to end at, if ets is not set.",
    )
    month2: int = Field(
        default=None,
        description="Month to end at, if ets is not set.",
    )
    day2: int = Field(
        default=None,
        description="Day to end at, if ets is not set.",
    )
    hour2: int = Field(
        default=None,
        description="Hour to end at, if ets is not set.",
    )
    minute2: int = Field(
        default=None,
        description="Minute to end at, if ets is not set.",
    )


@iemapp(default_tz="America/Chicago", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go do something"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing GET parameter sts or ets")
    include_latlon = environ["gis"]
    myvars = environ["vars"]
    delimiter = DELIMITERS[environ["delim"]]
    what = environ["what"]
    tzname = environ["tz"]
    src = environ["src"]
    stations = environ["stations"]
    if not stations:
        raise IncompleteWebRequest("Missing GET parameter stations=")

    tbl = "alldata"
    if src in ["soil", "traffic"]:
        tbl = f"alldata_{src}"
    network = environ["network"]
    nt = NetworkTable(network, only_online=False)
    if "_ALL" in stations:
        stations = list(nt.sts.keys())
    params = {
        "tzname": tzname,
        "ids": stations,
        "sts": environ["sts"],
        "ets": environ["ets"],
    }
    sql = text(
        f"SELECT *, valid at time zone :tzname as obtime from {tbl} "
        "WHERE station = ANY(:ids) and valid BETWEEN :sts and :ets "
        "ORDER by valid ASC"
    )
    with get_sqlalchemy_conn("rwis") as conn:
        df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Sorry, no results found for query!"]
    # default is to include all variables
    if not environ["vars"]:
        myvars = list(df.columns)
        myvars.remove("station")
        myvars.remove("valid")
        myvars.remove("obtime")
    myvars.insert(0, "station")
    myvars.insert(1, "obtime")
    if include_latlon:
        myvars.insert(2, "longitude")
        myvars.insert(3, "latitude")

        def get_lat(station):
            """hack"""
            return nt.sts[station]["lat"]

        def get_lon(station):
            """hack"""
            return nt.sts[station]["lon"]

        df["latitude"] = [get_lat(x) for x in df["station"]]
        df["longitude"] = [get_lon(x) for x in df["station"]]

    sio = StringIO()
    if what in ["txt", "download"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=rwis.txt"),
        ]
        start_response("200 OK", headers)
        df.to_csv(sio, index=False, sep=delimiter, columns=myvars)
        return [sio.getvalue().encode("ascii")]
    if what == "html":
        start_response("200 OK", [("Content-type", "text/html")])
        df.to_html(sio, columns=myvars)
        return [sio.getvalue().encode("ascii")]
    if what == "excel":
        if len(df.index) >= 1048576:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"Dataset too large for excel format."]
        bio = BytesIO()
        with pd.ExcelWriter(bio) as writer:
            df.to_excel(writer, sheet_name="Data", index=False, columns=myvars)

        headers = [
            ("Content-type", EXL),
            ("Content-disposition", "attachment; Filename=rwis.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]
    start_response("200 OK", [("Content-type", "text/plain")])
    df.to_csv(
        path_or_buf=sio,
        sep=delimiter,
        columns=df.columns.intersection(myvars).tolist(),
    )
    return [sio.getvalue().encode("ascii")]
