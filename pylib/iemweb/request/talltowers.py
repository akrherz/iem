""".. title:: Tall Towers Data Request

Return to `API Services </api/#cgi>`_ or
`Download Frontend </projects/iao/analog_download.php>`_

Changelog
---------

- 2024-09-02: Initial documentation update and pydantic validation

Example Requests
----------------

Provide the hourly averaged data on 15 September 2016

https://mesonet.agron.iastate.edu/cgi-bin/request/talltowers.py?\
station=ETTI4,MCAI4&var=ws_s&var=ws_nw&z=10&z=2&agg=avg\
&sts=2016-09-15T00:00Z&ets=2016-09-16T00:00Z&window=60&format=excel

Same request, but return as a CSV file

https://mesonet.agron.iastate.edu/cgi-bin/request/talltowers.py?\
station=ETTI4,MCAI4&var=ws_s&var=ws_nw&z=10&z=2&agg=avg\
&sts=2016-09-15T00:00Z&ets=2016-09-16T00:00Z&window=60&format=comma

"""

from datetime import timedelta
from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from pydantic import AwareDatetime, Field
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    TZ_FIELD,
    YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

TOWERIDS = {0: "ETTI4", 1: "MCAI4"}


class Schema(CGIModel):
    """See how we are called."""

    agg: Annotated[
        ListOrCSVType,
        Field(
            default_factory=lambda: ["avg"],
            description="Aggregation method to use",
        ),
    ]
    format: Annotated[
        str,
        Field(
            description="The format of the response",
            pattern="^(excel|tdf|comma)$",
        ),
    ] = "excel"
    ets: Annotated[
        AwareDatetime | None,
        Field(
            description="End of the period of interest",
        ),
    ] = None
    sts: Annotated[
        AwareDatetime | None,
        Field(
            description="Start of the period of interest",
        ),
    ] = None
    station: ListOrCSVType = Field(..., description="Station(s) to query")
    var: Annotated[
        ListOrCSVType,
        Field(
            description="Variable(s) to query",
        ),
    ]
    window: Annotated[
        int,
        Field(
            description="Window size for aggregation",
            ge=1,
            le=1440,
        ),
    ] = 1
    z: Annotated[ListOrCSVType, Field(description="Height(s) to query")]
    tz: TZ_FIELD = "Etc/UTC"
    year1: YEAR_FIELD_OPTIONAL
    month1: MONTH_FIELD_OPTIONAL
    day1: DAY_OF_MONTH_FIELD_OPTIONAL
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: YEAR_FIELD_OPTIONAL
    month2: MONTH_FIELD_OPTIONAL
    day2: DAY_OF_MONTH_FIELD_OPTIONAL
    hour2: HOUR_FIELD = 0
    minute2: MINUTE_FIELD = 0


def get_stations(environ):
    """Figure out the requested station"""
    towers = []
    for tid, nwsli in TOWERIDS.items():
        if nwsli in environ["station"]:
            towers.append(tid)

    return towers


def get_columns(cursor):
    """What have we here."""
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name   = 'data_analog'"
    )
    res = [row[0] for row in cursor]
    return res


@iemapp(help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go main Go"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start/end time")
    pgconn = get_dbconn("talltowers")
    columns = get_columns(pgconn.cursor())
    tzname = environ["tz"]

    stations = get_stations(environ)
    if not stations:
        raise IncompleteWebRequest("No stations")
    sts = environ["sts"]
    ets = environ["ets"]
    if (ets - sts) > timedelta(days=31):
        ets = sts + timedelta(days=31)
    fmt = environ["format"]
    # Build out our variable list
    tokens = []
    zz = environ["z"]
    varnames = environ["var"]
    aggs = environ["agg"]
    for z in zz:
        for v in varnames:
            v1 = v
            v2 = ""
            if v.find("_") > -1:
                v1, v2 = v.split("_")
                v2 = f"_{v2}"
            colname = f"{v1}_{z}m{v2}"
            if colname not in columns:
                continue
            for agg in aggs:
                if agg not in ["avg", "max", "min", "sum", "stddev"]:
                    raise IncompleteWebRequest(f"Invalid agg {agg}")
                tokens.append(f"{agg}({colname}) as {colname}_{agg}")
    if not tokens:
        raise IncompleteWebRequest("No variables selected")

    tw = environ["window"]

    sql = f"""
    SELECT tower,
    (date_trunc('hour', valid) +
    (((date_part('minute', valid)::integer / {tw}::integer) * {tw}::integer)
     || ' minutes')::interval) at time zone :tz as ts,
    {",".join(tokens)} from
    data_analog where tower = ANY(:sids) and valid >= :sts and valid < :ets
    GROUP by tower, ts ORDER by tower, ts
    """
    with get_sqlalchemy_conn("talltowers") as conn:
        df = pd.read_sql(
            sql_helper(sql),
            conn,
            params={"tz": tzname, "sids": stations, "sts": sts, "ets": ets},
        )
    df = df.rename(columns={"ts": "valid"})
    df["tower"] = df["tower"].replace(TOWERIDS)
    pgconn.close()
    if fmt in ["tdf", "comma"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=talltowers.txt"),
        ]
        start_response("200 OK", headers)
        sio = StringIO()
        df.to_csv(sio, sep="," if fmt == "comma" else "\t", index=False)
        return [sio.getvalue().encode("utf8")]

    # Excel
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Data", index=False)
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=talltowers.xlsx"),
    ]
    start_response("200 OK", headers)
    return bio.getvalue()
