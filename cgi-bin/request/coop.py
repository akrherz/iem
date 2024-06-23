""".. title:: IEM Climodat Data Export

Documentation for /cgi-bin/request/coop.py
------------------------------------------

This service is somewhat poorly named ``coop.py``, but is providing the IEM
Climodat data, which is a combination of NWS COOP and NWS ASOS/AWOS data. There
are a number of knobs here as this is one of the most popular datasets the IEM
produces.

Changelog
---------

- 2024-06-22: Initital documentation and backend conversion to pydantic.

"""

import datetime

from iemweb.request.coop import (
    do_apsim,
    do_century,
    do_daycent,
    do_dndc,
    do_salus,
    do_simple,
    do_swat,
)
from metpy.units import units
from pydantic import Field
from pyiem.database import get_dbconnc
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

DEGC = units.degC
DEGF = units.degF
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class Schema(CGIModel):
    """See how we are called."""

    delim: str = Field(
        "comma",
        description=(
            "The delimiter to use in the output file.  "
            "Options: comma, tab, space"
        ),
    )
    gis: bool = Field(
        False,
        description="Include latitude and longitude columns in the output.",
    )
    inclatlon: bool = Field(
        False,
        description="Include latitude and longitude columns in the output.",
    )
    model: str = Field(
        None,
        description=(
            "The model to use for output.  Options: simple, apsim, "
            "century, daycent, salus, dndc, swat.  Specifying this will "
            "override the 'vars' option."
        ),
    )
    network: str = Field(
        "IACLIMATE", description="The network to use for station lookups."
    )
    scenario: bool = Field(
        False,
        description=(
            "Should data from a previous year, specified by scenario_year "
            "be used to fill out the present year."
        ),
    )
    scenario_year: int = Field(
        2020,
        description=(
            "The year to use as a scenario year, if scenario is true."
        ),
    )
    station: ListOrCSVType = Field(
        [], description="List of stations to include in the output."
    )
    stations: ListOrCSVType = Field(
        [],
        description=(
            "List of stations to include in the output. Legacy variable name."
        ),
    )
    vars: ListOrCSVType = Field(
        [], description="List of variables to include in the output."
    )
    what: str = Field("view", description="The type of output to generate.")
    with_header: bool = Field(
        True, description="Include a header row in the output."
    )
    year1: int = Field(
        datetime.date.today().year,
        description="The starting year for the data request.",
    )
    month1: int = Field(
        1,
        description="The starting month for the data request.",
    )
    day1: int = Field(
        1,
        description="The starting day for the data request.",
    )
    year2: int = Field(
        datetime.date.today().year,
        description="The ending year for the data request.",
    )
    month2: int = Field(
        datetime.date.today().month,
        description="The ending month for the data request.",
    )
    day2: int = Field(
        datetime.date.today().day,
        description="The ending day for the data request.",
    )


def get_scenario_period(ctx):
    """Compute the inclusive start and end dates to fetch scenario data for
    Arguments:
        ctx dictionary context this app was called with
    """
    if ctx["ets"].month == 2 and ctx["ets"].day == 29:
        sts = datetime.date(ctx["scenario_year"], ctx["ets"].month, 28)
    else:
        sts = datetime.date(
            ctx["scenario_year"], ctx["ets"].month, ctx["ets"].day
        )
    ets = datetime.date(ctx["scenario_year"], 12, 31)
    return sts, ets


def sane_date(year, month, day):
    """Attempt to account for usage of days outside of the bounds for
    a given month"""
    # Calculate the last date of the given month
    nextmonth = datetime.date(year, month, 1) + datetime.timedelta(days=35)
    lastday = nextmonth.replace(day=1) - datetime.timedelta(days=1)
    return datetime.date(year, month, min(day, lastday.day))


def get_cgi_dates(environ):
    """Figure out which dates are requested via the form, we shall attempt
    to account for invalid dates provided!"""

    ets = min(
        sane_date(environ["year2"], environ["month2"], environ["day2"]),
        datetime.date.today() - datetime.timedelta(days=1),
    )

    return [
        sane_date(environ["year1"], environ["month1"], environ["day1"]),
        ets,
    ]


def get_cgi_stations(environ):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = environ["station"]
    if not reqlist:
        reqlist = environ["stations"]
    if not reqlist:
        return []
    if "_ALL" in reqlist:
        network = environ["network"]
        nt = NetworkTable(network, only_online=False)
        return list(nt.sts.keys())

    return reqlist


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """go main go"""
    ctx = {}
    ctx["stations"] = get_cgi_stations(environ)
    if not ctx["stations"]:
        raise IncompleteWebRequest("No stations were specified.")
    ctx["sts"], ctx["ets"] = get_cgi_dates(environ)
    ctx["myvars"] = environ["vars"]
    # Model specification trumps vars[]
    if environ["model"] is not None:
        ctx["myvars"] = [environ["model"]]
    ctx["what"] = environ["what"]
    ctx["delim"] = environ["delim"]
    ctx["inclatlon"] = environ["gis"]
    ctx["scenario"] = environ["scenario"]
    ctx["scenario_year"] = 2099
    if ctx["scenario"] == "yes":
        ctx["scenario_year"] = environ["scenario_year"]
    ctx["scenario_sts"], ctx["scenario_ets"] = get_scenario_period(ctx)
    ctx["with_header"] = environ["with_header"]

    # TODO: this code stinks and is likely buggy
    headers = []
    if (
        "apsim" in ctx["myvars"]
        or "daycent" in ctx["myvars"]
        or "century" in ctx["myvars"]
        or "salus" in ctx["myvars"]
    ):
        if ctx["what"] == "download":
            headers.append(("Content-type", "application/octet-stream"))
            headers.append(
                ("Content-Disposition", "attachment; filename=metdata.txt")
            )
        else:
            headers.append(("Content-type", "text/plain"))
    elif "dndc" not in ctx["myvars"] and ctx["what"] != "excel":
        if ctx["what"] == "download":
            headers.append(("Content-type", "application/octet-stream"))
            dlfn = "changeme.txt"
            if len(ctx["stations"]) < 10:
                dlfn = f"{'_'.join(ctx['stations'])}.txt"
            headers.append(
                ("Content-Disposition", f"attachment; filename={dlfn}")
            )
        else:
            headers.append(("Content-type", "text/plain"))
    elif "dndc" in ctx["myvars"]:
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=dndc.zip")
        )
    elif "swat" in ctx["myvars"]:
        headers.append(("Content-type", "application/octet-stream"))
        headers.append(
            ("Content-Disposition", "attachment; filename=swatfiles.zip")
        )
    elif ctx["what"] == "excel":
        headers.append(("Content-type", EXL))
        headers.append(
            ("Content-Disposition", "attachment; filename=nwscoop.xlsx")
        )

    conn, cursor = get_dbconnc("coop")
    start_response("200 OK", headers)
    # OK, now we fret
    if "daycent" in ctx["myvars"]:
        res = do_daycent(cursor, ctx)
    elif "century" in ctx["myvars"]:
        res = do_century(cursor, ctx)
    elif "apsim" in ctx["myvars"]:
        res = do_apsim(cursor, ctx)
    elif "dndc" in ctx["myvars"]:
        res = do_dndc(cursor, ctx)
    elif "salus" in ctx["myvars"]:
        res = do_salus(cursor, ctx)
    elif "swat" in ctx["myvars"]:
        res = do_swat(None, ctx)
    else:
        res = do_simple(cursor, ctx)
    cursor.close()
    conn.close()
    return [res]
