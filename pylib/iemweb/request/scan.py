""".. title:: SCAN Data Request

Return to `Request frontend </request/scan/fe.phtml>`_ or
`API Services </api/#cgi>`_

Documentation for /cgi-bin/request/scan.py
------------------------------------------

This application provides a simple interface to download SCAN data for a
specified period of time.  The data is returned in a simple text format that
can be easily imported into a spreadsheet or other data analysis software.

Changelog
---------

- 2025-02-23: Initial implementation

Example Requests
----------------

Get all SCAN data for 2024

https://mesonet.agron.iastate.edu/cgi-bin/request/scan.py?\
stations=_ALL&sts=2024-01-01&ets=2025-01-01&&what=dl&delim=comma

"""

from io import StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}


class Schema(CGIModel):
    """See how we are called."""

    stations: ListOrCSVType = Field(
        ..., description="List of SCAN station identifiers."
    )
    vars: ListOrCSVType = Field(
        ..., description="List of variables to include in the output."
    )
    sts: str = Field(None, description="Start of the period of interest.")
    ets: str = Field(None, description="End of the period of interest.")
    delim: str = Field(
        "comma",
        description="Delimiter to use in the output file.",
        pattern="^(comma|space|tab)$",
    )
    what: str = Field(
        "dl",
        description="Download or view.",
    )
    year1: int = Field(
        None,
        description="Start year when sts is not provided.",
    )
    month1: int = Field(
        None,
        description="Start month when sts is not provided.",
    )
    day1: int = Field(
        None,
        description="Start day when sts is not provided.",
    )
    hour1: int = Field(
        None,
        description="Start hour when sts is not provided.",
    )
    year2: int = Field(
        None,
        description="End year when ets is not provided.",
    )
    month2: int = Field(
        None,
        description="End month when ets is not provided.",
    )
    day2: int = Field(
        None,
        description="End day when ets is not provided.",
    )
    hour2: int = Field(
        None,
        description="End hour when ets is not provided.",
    )


def get_cgi_stations(environ):
    """Figure out which stations the user wants, return a list of them"""
    reqlist = environ["stations"]
    if "_ALL" in reqlist:
        nt = NetworkTable("SCAN", only_online=False)
        return list(nt.sts.keys())

    return reqlist


def get_df(environ: dict) -> pd.DataFrame:
    """Get what the database has!"""
    with get_sqlalchemy_conn("scan") as conn:
        df = pd.read_sql(
            sql_helper(
                "select * from alldata where station = ANY(:ids) and "
                "valid >= :sts and valid < :ets "
                "order by station asc, valid asc"
            ),
            conn,
            params={
                "ids": environ["stations"],
                "sts": environ["sts"],
                "ets": environ["ets"],
            },
        )
    if not df.empty:
        df["valid"] = df["valid"].dt.strftime("%Y-%m-%d %H:%M")
    return df


@iemapp(help=__doc__, schema=Schema, default_tz="UTC")
def application(environ, start_response):
    """
    Do something!
    """
    environ["stations"] = get_cgi_stations(environ)
    if (
        len(environ["stations"]) > 9
        and (environ["ets"] - environ["sts"]).days > 366
    ):
        raise IncompleteWebRequest(
            "You have requested too much data, please limit to 10 stations "
            "and 1 year of data."
        )
    varnames: list = environ["vars"]
    varnames.insert(0, "valid")
    varnames.insert(0, "station")
    what = environ["what"]
    df = get_df(environ)
    if what in ["txt", "download"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=scan.txt"),
        ]
    else:
        headers = [("Content-type", "text/plain")]
    start_response("200 OK", headers)
    sio = StringIO()
    df.to_csv(
        sio, index=False, sep=DELIMITERS[environ["delim"]], columns=varnames
    )
    return [sio.getvalue().encode("ascii")]
