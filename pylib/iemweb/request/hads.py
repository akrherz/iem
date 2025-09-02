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

Example Requests
----------------

Request all Iowa DCP data, which is limited to a 24 hour period.

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=_ALL&network=IA_DCP&sts=2023-11-10T00:00Z&ets=2023-11-11T00:00Z\
&what=dl

Provide all DNKI4 data for the month of November 2023

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=DNKI4&sts=2023-11-01T00:00Z&ets=2023-12-01T00:00Z&what=txt

Same request, but in HTML format

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=DNKI4&sts=2023-11-01T00:00Z&ets=2023-12-01T00:00Z&what=html

Same request, but in Excel format

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=DNKI4&sts=2023-11-01T00:00Z&ets=2023-12-01T00:00Z&what=excel

Provide all DSXI4 data for 1 Jan 2025

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=DSXI4&sts=2025-01-01T00:00Z&ets=2025-01-02T00:00Z&what=txt

Run the threshold search for when HGIRG exceeds 10.81
for AESI4 in early Sep 2025

https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?\
stations=AESI4&sts=2025-09-01T00:00Z&ets=2025-09-03T00:00Z&what=txt&\
threshold=10.81&thresholdvar=RG

"""

from datetime import timedelta
from io import BytesIO, StringIO

import pandas as pd
from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

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
    threshold: float | None = Field(
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
    year1: int | None = Field(
        None,
        description="Start year for request, when sts not set.",
    )
    year2: int | None = Field(
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
    @classmethod
    def check_threshold(cls, value):
        """Allow empty string."""
        return None if value == "" else value


def threshold_search(table: pd.DataFrame, threshold, thresholdvar: str):
    """Do the threshold searching magic"""
    cols = table.columns.to_list()
    searchfor = f"HGI{thresholdvar.upper()}ZZ"
    if searchfor not in cols:
        return pd.DataFrame()
    above = False
    maxrunning = -99
    maxvalid = None
    res = []
    for (station, valid), row in table.iterrows():
        val = row[searchfor]
        if val > threshold and not above:
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="START",
                    value=val,
                    varname=searchfor,
                )
            )
            above = True
        if val > threshold and above and val > maxrunning:
            maxrunning = val
            maxvalid = valid
        if val < threshold and above:
            res.append(
                dict(
                    station=station,
                    utc_valid=maxvalid,
                    event="MAX",
                    value=maxrunning,
                    varname=searchfor,
                )
            )
            res.append(
                dict(
                    station=station,
                    utc_valid=valid,
                    event="END",
                    value=val,
                    varname=searchfor,
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
        stations = list(
            NetworkTable(environ["network"][:10], only_online=False).sts.keys()
        )
        environ["ets"] = min(
            environ["ets"], environ["sts"] + timedelta(hours=24)
        )
    if len(stations) > 1 and (environ["ets"] - environ["sts"]) > timedelta(
        days=365
    ):
        raise IncompleteWebRequest(
            "Error, more than one station and more than 365 days requested"
        )
    if not stations:
        raise IncompleteWebRequest("Error, no stations specified!")
    sql = sql_helper(
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
    if (
        environ["threshold"] is not None
        and environ["thresholdvar"] is not None
    ):
        if len(stations) > 1:
            start_response("200 OK", [("Content-type", "text/plain")])
            return [b"Can not do threshold search for more than one station"]
        table = threshold_search(
            table, environ["threshold"], environ["thresholdvar"]
        )

    if environ["what"] == "html":
        headers = [("Content-type", "text/html")]
        start_response("200 OK", headers)
        sio = StringIO()
        table.to_html(sio)
        return [sio.getvalue().encode("utf-8")]
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
    # The default for what = dl and txt
    sio = StringIO()
    headers = [
        ("Content-type", "application/octet-stream"),
        ("Content-Disposition", "attachment; filename=hads.txt"),
    ]
    start_response("200 OK", headers)
    table.to_csv(sio, sep=delimiter)
    return [sio.getvalue().encode("utf-8")]
