""".. title:: HADS Data Request

`IEM API Mainpage </api/#cgi>`_

Documentation on /cgi-bin/request/hads.py
-----------------------------------------

The backend database for this application has many billion rows of data, so
requests can be slow.

Changelog
---------

- 2024-04-18: Allowed cross-year requests, but limited to 365 days when
  requesting more than one station.
- 2024-04-09: Migrated to pydantic based CGI field validation.
- 2024-03-15: Initial documentation added

"""

# pylint: disable=abstract-class-instantiated
from datetime import timedelta
from io import BytesIO, StringIO
from typing import Optional

import pandas as pd
from pydantic import AwareDatetime, Field, field_validator
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
        "comma",
        description="Delimiter for output",
        pattern="^(comma|space|tab)$",
    )
    ets: AwareDatetime = Field(None, description="End Time for request")
    network: str = Field(None, description="Network Identifier")
    stations: ListOrCSVType = Field(..., description="Station Identifier(s)")
    sts: AwareDatetime = Field(None, description="Start Time for request")
    threshold: Optional[float] = Field(
        None, description="Threshold Value for Searching"
    )
    thresholdvar: str = Field(
        None,
        description="Threshold Variable for Searching",
        pattern="^(RG|PCP)$",
    )
    what: str = Field(
        "dl", description="Output format", pattern="^(dl|txt|html|excel)$"
    )
    year: int = Field(
        None,
        description=(
            "Legacy year value when this service only supported 1 year at a "
            "time."
        ),
    )
    year1: Optional[int] = Field(
        None,
        description="Start year for request, when sts not set.",
    )
    year2: Optional[int] = Field(
        None,
        description="End year for request, when ets not set.",
    )
    month1: int = Field(
        None,
        description="Start month for request, when sts not set.",
    )
    month2: int = Field(
        None,
        description="End month for request, when ets not set.",
    )
    day1: int = Field(
        None,
        description="Start day for request, when sts not set.",
    )
    day2: int = Field(
        None,
        description="End day for request, when ets not set.",
    )
    hour1: int = Field(
        0,
        description="Start hour for request, when sts not set.",
    )
    hour2: int = Field(
        0,
        description="End hour for request, when ets not set.",
    )
    minute1: int = Field(
        0,
        description="Start minute for request, when sts not set.",
    )
    minute2: int = Field(
        0,
        description="End minute for request, when ets not set.",
    )

    @field_validator("threshold", mode="before")
    def check_threshold(cls, value):
        """Allow empty string."""
        return None if value == "" else value


def threshold_search(table, threshold, thresholdvar):
    """Do the threshold searching magic"""
    cols = list(table.columns.values)
    searchfor = f"HGI{thresholdvar.upper()}"
    cols5 = [s[:5] for s in cols]
    mycol = cols[cols5.index(searchfor)]
    above = False
    maxrunning = -99
    maxvalid = None
    res = []
    for (station, valid), row in table.iterrows():
        val = row[mycol]
        if val > threshold and not above:
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="START",
                    value=val,
                    varname=mycol,
                )
            )
            above = True
        if val > threshold and above:
            if val > maxrunning:
                maxrunning = val
                maxvalid = valid
        if val < threshold and above:
            res.append(
                dict(
                    station=station,
                    utc_valid=maxvalid,
                    event="MAX",
                    value=maxrunning,
                    varname=mycol,
                )
            )
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="END",
                    value=val,
                    varname=mycol,
                )
            )
            above = False
            maxrunning = -99
            maxvalid = None

    return pd.DataFrame(res)


@iemapp(default_tz="UTC", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go do something"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Error, missing start or end time")
    delimiter = DELIMITERS[environ["delim"]]
    stations = environ["stations"]
    if "_ALL" in stations and environ["network"] is not None:
        stations = list(NetworkTable(environ["network"][:10]).sts.keys())
        if (environ["ets"] - environ["sts"]) > timedelta(hours=24):
            environ["ets"] = environ["sts"] + timedelta(hours=24)
    if len(stations) > 1 and (environ["ets"] - environ["sts"]) > timedelta(
        days=365
    ):
        raise IncompleteWebRequest(
            "Error, more than one station and more than 365 days requested"
        )
    if not stations:
        raise IncompleteWebRequest("Error, no stations specified!")
    sql = text(
        """
        SELECT station, valid at time zone 'UTC' as utc_valid, key, value
        from raw WHERE station = ANY(:ids) and
        valid BETWEEN :sts and :ets and value > -999
        ORDER by valid ASC
        """
    )
    params = {"ids": stations, "sts": environ["sts"], "ets": environ["ets"]}

    with get_sqlalchemy_conn("hads") as conn:
        df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Error, no results found for query!"]
    table = df.pivot_table(
        values="value", columns=["key"], index=["station", "utc_valid"]
    )
    if environ["threshold"] is not None:
        if len(stations) > 1:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"Can not do threshold search for more than one station"]
        table = threshold_search(
            table, environ["threshold"], environ["thresholdvar"]
        )

    sio = StringIO()
    if environ["what"] == "txt":
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-Disposition", "attachment; filename=hads.txt"),
        ]
        start_response("200 OK", headers)
        table.to_csv(sio, sep=delimiter)
        return [sio.getvalue().encode("ascii")]
    if environ["what"] == "html":
        headers = [("Content-type", "text/html")]
        start_response("200 OK", headers)
        table.to_html(sio)
        return [sio.getvalue().encode("ascii")]
    if environ["what"] == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            table.to_excel(writer, sheet_name="Data", index=True)

        headers = [
            ("Content-type", EXL),
            ("Content-Disposition", "attachment; filename=hads.xlsx"),
        ]
        start_response("200 OK", headers)
        return [bio.getvalue()]
    start_response("200 OK", [("Content-type", "text/plain")])
    table.to_csv(sio, sep=delimiter)
    return [sio.getvalue().encode("ascii")]
