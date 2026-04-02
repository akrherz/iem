""".. title:: RWIS Download

Return to `API Services </api/#cgi>`_ and
`RWIS Download Portal </request/rwis/fe.phtml>`_

Documentation for /cgi-bin/request/rwis.py
------------------------------------------

This service emits RWIS data.

Changelog
---------

- 2026-03-17: When requesting text/csv output, you can request up to
  500 station-years worth of data.  If you are requesting Excel or HTML
  output, you are limited to 1 station-years to prevent this service from
  exhausting resources.
- 2025-02-26: Added variable support for `relh` and `feel`, but these
  variables are not fully available yet over the archive.
- 2024-09-19: Fix bug with no variables returned when ``vars`` is not set
- 2024-08-01: Initital documentation release and pydantic validation

Example Requests
----------------

Provide all Iowa RWIS data for 1 July 2024 in Excel format:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=_ALL&tz=America%2FChicago&what=excel&src=atmos&\
sts=2024-07-01T00:00&ets=2024-07-02T00:00

Same request, but add a latitude and longitude column

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=_ALL&tz=America%2FChicago&what=excel&src=atmos&\
sts=2024-07-01T00:00&ets=2024-07-02T00:00&gis=true

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

Provide air temp and relative humidity data on 1 July 2024 for Iowa RWIS
stations RAKI4 in a text file:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=IA_RWIS&\
stations=RAKI4&tz=America%2FChicago&what=txt&src=atmos&\
sts=2024-07-01T00:00:00&ets=2024-07-02T00:00:00&vars=tmpf,relh

Provide all atmospheric data for 31 July 2024 in UTC timezone for
Minnesota RWIS stations:

https://mesonet.agron.iastate.edu/cgi-bin/request/rwis.py?network=MN_RWIS&\
stations=_ALL&tz=UTC&what=download&src=atmos&\
sts=2024-07-31T00:00&ets=2024-08-01T00:00

"""

from datetime import datetime
from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import DateTime, String, bindparam
from sqlalchemy.dialects.postgresql import ARRAY

from iemweb.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD_OPTIONAL,
    MINUTE_FIELD_OPTIONAL,
    MONTH_FIELD_OPTIONAL,
    NETWORK_FIELD,
    STATION_LIST_FIELD,
    TZ_FIELD_OPTIONAL,
    YEAR_FIELD_OPTIONAL,
)

DELIMITERS = {"comma": ",", "space": " ", "tab": "\t"}
EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
FIXED_COLUMNS = ("station", "obtime")
GIS_COLUMNS = ("longitude", "latitude")
EXCLUDED_DB_COLUMNS = ("iemid", "valid")


class Schema(CGIModel):
    """See how we are called."""

    delim: Annotated[
        str,
        Field(
            description="Delimiter to use in output file",
            pattern="^(comma|space|tab)$",
        ),
    ] = "comma"
    gis: Annotated[
        bool,
        Field(
            description="Include latitude and longitude columns in output",
        ),
    ] = False
    vars: Annotated[
        ListOrCSVType,
        Field(
            default_factory=list,
            description=(
                "List of variables to include in output, if none are set, "
                "then all variables are returned for the given ``src``"
            ),
        ),
    ]
    what: Annotated[
        str,
        Field(
            description=(
                "Controls the response format.  `dl` and `txt` provide data "
                "in a delimited text file, `html` provides a HTML table, "
                "`excel` provides the data in a Microsoft Excel format. "
            ),
            pattern="^(dl|txt|html|excel|download)$",
        ),
    ] = "dl"
    tz: TZ_FIELD_OPTIONAL = "UTC"
    src: Annotated[
        str,
        Field(
            description="Data source to use",
            pattern="^(atmos|soil|traffic)$",
        ),
    ] = "atmos"
    stations: STATION_LIST_FIELD
    network: NETWORK_FIELD = "IA_RWIS"
    sts: Annotated[
        datetime | None,
        Field(
            description="Start timestamp",
        ),
    ] = None
    ets: Annotated[
        datetime | None,
        Field(
            description="End timestamp",
        ),
    ] = None
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD_OPTIONAL = None
    minute1: MINUTE_FIELD_OPTIONAL = None
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD_OPTIONAL = None
    minute2: MINUTE_FIELD_OPTIONAL = None


def compute_output_columns(
    available_columns: list[str],
    requested_columns: list[str],
    include_latlon: bool,
) -> tuple[list[str], list[str]]:
    """Sanitize requested columns and derive SQL/output column lists."""
    available_set = set(available_columns)
    data_columns = [
        col
        for col in available_columns
        if col not in (*FIXED_COLUMNS, *GIS_COLUMNS, *EXCLUDED_DB_COLUMNS)
    ]
    if requested_columns:
        query_columns = []
        for col in requested_columns:
            if col in data_columns and col not in query_columns:
                query_columns.append(col)
    else:
        query_columns = data_columns

    output_columns = list(FIXED_COLUMNS)
    if include_latlon and all(col in available_set for col in GIS_COLUMNS):
        output_columns.extend(GIS_COLUMNS)
    output_columns.extend(
        col for col in query_columns if col not in output_columns
    )
    return output_columns, query_columns


@iemapp(default_tz="America/Chicago", help=__doc__, schema=Schema)
def application(environ, start_response):
    """Go do something"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing GET parameter sts or ets")
    include_latlon = environ["gis"]
    requested_columns = environ["vars"]
    delimiter = DELIMITERS[environ["delim"]]
    what = environ["what"]
    tzname = environ["tz"]
    src = environ["src"]
    stations = environ["stations"]
    if not stations:
        raise IncompleteWebRequest("Missing GET parameter stations=")

    table = "alldata"
    if src in ["soil", "traffic"]:
        table = f"alldata_{src}"
    network = environ["network"]
    if "_ALL" in stations:
        nt = NetworkTable(network, only_online=False)
        stations = list(nt.sts.keys())
    size_limit = 500 if what in ["txt", "download", "dl"] else 1
    this_size = len(stations) * (
        (environ["ets"] - environ["sts"]).days / 366.0
    )
    if this_size > size_limit:
        raise IncompleteWebRequest(
            f"Requested {this_size:.1f} station-years of data, which exceeds "
            f"the limit of {size_limit} station-years for the requested "
            f"format. Please reduce the number of stations or the time range."
        )
    params = {
        "tzname": tzname,
        "ids": stations,
        "sts": environ["sts"],
        "ets": environ["ets"],
    }
    available_select = [
        "t.id as station",
        "valid at time zone :tzname as obtime",
    ]
    if include_latlon:
        available_select.extend(
            ["ST_X(geom) as longitude", "ST_Y(geom) as latitude"]
        )
    available_select.append("a.*")
    # Generate a cheap query to figure out the columns and if data
    # even exists.
    sql = sql_helper(
        """SELECT {selectcols} from
        {table} a JOIN stations t on (a.iemid = t.iemid)
        WHERE t.id = any(:ids) and valid >= :sts and valid < :ets
        limit 1""",
        table=table,
        selectcols=", ".join(available_select),
    )
    with get_sqlalchemy_conn("rwis") as conn:
        df = pd.read_sql(sql, conn, params=params)
    if df.empty:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Sorry, no results found for query!"]
    output_columns, query_columns = compute_output_columns(
        df.columns.tolist(), requested_columns, include_latlon
    )

    select_columns = [
        "t.id as station",
        "valid at time zone :tzname as obtime",
    ]
    if include_latlon and all(col in output_columns for col in GIS_COLUMNS):
        select_columns.extend(
            ["ST_X(geom) as longitude", "ST_Y(geom) as latitude"]
        )
    select_columns.extend(query_columns)

    sql = sql_helper(
        """
        SELECT {selectcols} from
        {table} a JOIN stations t on (a.iemid = t.iemid)
        WHERE t.id = any(:ids) and valid >= :sts and valid < :ets
        ORDER by valid ASC
                """,
        table=table,
        selectcols=", ".join(select_columns),
    )

    if what in ["txt", "download", "dl"]:
        headers = [
            ("Content-type", "application/octet-stream"),
            ("Content-disposition", "attachment; filename=rwis.txt"),
        ]
        start_response("200 OK", headers)

        def stream_copy():
            with get_sqlalchemy_conn("rwis") as conn:
                compiled = sql.bindparams(
                    bindparam("tzname", value=tzname, type_=String()),
                    bindparam("ids", value=stations, type_=ARRAY(String())),
                    bindparam("sts", value=environ["sts"], type_=DateTime()),
                    bindparam("ets", value=environ["ets"], type_=DateTime()),
                ).compile(
                    conn,
                    compile_kwargs={
                        "literal_binds": True,
                        "render_postcompile": True,
                    },
                )
                copy_delimiter = "','"
                if delimiter == "\t":
                    copy_delimiter = r"E'\t'"
                elif delimiter == " ":
                    copy_delimiter = "' '"
                cursor = conn.connection.cursor()
                with cursor.copy(
                    "COPY ("
                    f"{compiled}"
                    ") TO STDOUT WITH (FORMAT CSV, HEADER TRUE, "
                    f"DELIMITER {copy_delimiter})"
                ) as copy:
                    for chunk in copy:
                        yield bytes(chunk)

        return stream_copy()

    # Now we depend on pandas to do some magic
    with get_sqlalchemy_conn("rwis") as conn:
        df = pd.read_sql(sql, conn, params=params)

    if what == "html":
        sio = StringIO()
        start_response("200 OK", [("Content-type", "text/html")])
        df.to_html(sio, index=False, columns=output_columns)
        return [sio.getvalue().encode("ascii")]

    # We are left with Excel
    if len(df.index) >= 1048576:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"Dataset too large for excel format."]
    bio = BytesIO()
    with pd.ExcelWriter(bio) as writer:
        df.to_excel(
            writer, sheet_name="Data", index=False, columns=output_columns
        )

    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=rwis.xlsx"),
    ]
    start_response("200 OK", headers)
    return [bio.getvalue()]
