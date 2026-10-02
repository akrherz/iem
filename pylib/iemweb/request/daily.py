""".. title:: IEM Computed Daily Summaries

Return to `API Services </api/#cgi>`_

Documentation for /cgi-bin/request/daily.py
-------------------------------------------

This data source contains a combination of IEM computed calendar day summaries
and some more official totals with some sites reporting explicit values.  One
should also note that typically the airport stations are for a 24 hour period
over standard time, which means 1 AM to 1 AM daylight time.

This service has a per-IP throttle requiring sequential requests with a two
second sleep between requests.

Changelog
---------

- 2026-10-02: The ``network`` parameter is now optional allowing for the
  service to dump everything for a single date at a time.  The service
  ignores any end date parameters in this usage case.  Additionally, this
  request will result in climatology variables **not** being included.
- 2026-10-02: The IEM ``network`` identifier is now included within the
  response to help with disambiguing the station identifier that is sometimes
  shared between networks.  The IEM enforces unique station+network
  identifiers.
- 2026-02-26: Address issue with non-ASCII characters breaking service (GIGO).

Example Usage
-------------

Request all IEM summary values for 15 January 2020.  Note that climatology
variables are not included with this request.

https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?sts=2020-01-15

Request all high temperature data for Ames, IA (AMW) for the month of January
2019:

https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?\
sts=2019-01-01&ets=2019-01-31&network=IA_ASOS&stations=AMW&\
var=max_temp_f&format=csv


Request daily precipitation and the climatology for all stations in Washington
state on 23 June 2023 in Excel format:

https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?\
sts=2023-06-23&ets=2023-06-23&network=WA_ASOS&\
var=precip_in,climo_precip_in&format=excel

"""

import copy
from datetime import datetime
from io import BytesIO, StringIO
from typing import Annotated

import pandas as pd
from pydantic import Field
from pyiem.database import get_dbconn, get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    MONTH_FIELD_OPTIONAL,
    NETWORK_FIELD,
    YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, ListOrCSVType, error_log, iemapp

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DEFAULT_COLS = (
    "max_temp_f,min_temp_f,max_dewpoint_f,min_dewpoint_f,precip_in,"
    "avg_wind_speed_kts,avg_wind_drct,min_rh,avg_rh,max_rh,"
    "climo_high_f,climo_low_f,climo_precip_in,snow_in,snowd_in,"
    "min_feel,avg_feel,max_feel,max_wind_speed_kts,max_wind_gust_kts,"
    "srad_mj"
).split(",")


class MyCGI(CGIModel):
    ets: Annotated[datetime | None, Field(description="End date to query")] = (
        None
    )
    format: Annotated[str, Field(description="The format of the output")] = (
        "csv"
    )
    na: Annotated[
        str,
        Field(
            description="The string representation of missing values.",
            pattern=r"^(?:None|M|blank)$",
        ),
    ] = "None"
    network: NETWORK_FIELD = ""
    station: Annotated[
        ListOrCSVType,
        Field(
            description=(
                "Comma delimited or multi-param station identifiers, _ALL "
                "for all stations in network (deprecated)"
            ),
            default_factory=list,
        ),
    ]
    stations: Annotated[
        ListOrCSVType,
        Field(
            description=(
                "Comma delimited or multi-param station identifiers, _ALL "
                "for all stations in network"
            ),
            default_factory=list,
        ),
    ]
    sts: Annotated[
        datetime | None, Field(description="Start date to query")
    ] = None
    var: Annotated[
        ListOrCSVType | None,
        Field(
            description=(
                "Comma delimited or multi-param variable names to include in "
                f"output, columns are: {DEFAULT_COLS}"
            ),
        ),
    ] = None
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None


def overloaded(environ: dict):
    """Prevent automation from overwhelming the server"""

    with get_dbconn("iem") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute("select one::float from system_loadavg")
        val = cursor.fetchone()[0]
    if val > 25:  # Cut back on logging
        error_log(environ, f"/cgi-bin/request/daily.py over cpu thres: {val}")
    return val > 20


def get_climate(network: str, stations: list[str]) -> str | pd.DataFrame:
    """Fetch the climatology for these stations"""
    nt = NetworkTable(network, only_online=False)
    if not nt.sts:
        return "ERROR: Invalid network specified"
    clisites = []
    for station in stations:
        if station == "_ALL":
            for sid in nt.sts:
                clid = nt.sts[sid]["ncei91"]
                if clid not in clisites:
                    clisites.append(clid)
            break
        if station not in nt.sts:
            return f"ERROR: station: {station} not found in network: {network}"
        clid = nt.sts[station]["ncei91"]
        if clid not in clisites:
            clisites.append(clid)
    with get_sqlalchemy_conn("coop") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            SELECT station, to_char(valid, 'mmdd') as sday,
            high as climo_high_f, low as climo_low_f,
            precip as climo_precip_in from ncei_climate91
            where station = ANY(:clisites)
            """
            ),
            conn,
            params={"clisites": clisites},
        )
    return df


def get_data(network: str, sts, ets, stations, cols, na, fmt: str):
    """Go fetch data please"""
    if not cols:
        cols = copy.deepcopy(DEFAULT_COLS)
    cols.insert(0, "day")
    cols.insert(0, "station")
    cols.append("network")
    climate = None
    # When network == "", we are getting everything for a single day!
    query_limiter = "s.day = :st"
    if network != "":
        query_limiter = (
            "s.day >= :st and s.day <= :et and t.network = :network "
            "and t.id = ANY(:ds)"
        )
        climate = get_climate(network, stations)
        if isinstance(climate, str):
            return climate

    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            sql_helper(
                """
            SELECT id as station, day, max_tmpf as max_temp_f,
            min_tmpf as min_temp_f, max_dwpf as max_dewpoint_f,
            min_dwpf as min_dewpoint_f,
            pday as precip_in,
            avg_sknt as avg_wind_speed_kts,
            vector_avg_drct as avg_wind_drct,
            min_rh, avg_rh, max_rh,
            snow as snow_in,
            snowd as snowd_in,
            min_feel, avg_feel, max_feel,
            max_sknt as max_wind_speed_kts,
            max_gust as max_wind_gust_kts,
            srad_mj, ncei91, to_char(day, 'mmdd') as sday, network
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE {query_limiter}
            ORDER by day, t.id ASC""",
                query_limiter=query_limiter,
            ),
            conn,
            params={"st": sts, "et": ets, "network": network, "ds": stations},
        )
    if climate is not None:
        # Join to climate data frame
        df = df.merge(
            climate,
            how="left",
            left_on=["ncei91", "sday"],
            right_on=["station", "sday"],
            suffixes=("", "_r"),
        )
    df = df[df.columns.intersection(cols)]
    if na != "blank":
        df = df.fillna(na)
    if fmt == "json":
        return df.to_json(orient="records", date_format="iso")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=MyCGI, parse_times=True, ip_throttle_secs=1.0)
def application(environ, start_response):
    """See how we are called"""
    query: MyCGI = environ["_cgimodel_schema"]
    if query.sts is None:
        raise IncompleteWebRequest("Missing required start time information.")
    if query.ets is None:
        if query.network != "":
            raise IncompleteWebRequest("Required end time missing.")
        query.ets = query.sts
    sts, ets = query.sts.date(), query.ets.date()

    if sts.year != ets.year and overloaded(environ):
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]

    stations = environ["stations"]
    if not stations:
        stations = environ["station"]
    if not stations and query.network != "":
        stations = ["_ALL"]
    network = environ["network"][:20]
    if "_ALL" in stations:
        if (ets - sts).days > 366:
            raise IncompleteWebRequest(
                "Must request a year or less when requesting all stations"
            )
        stations = list(NetworkTable(network, only_online=False).sts.keys())
    cols = environ["var"]
    na = environ["na"]
    if query.format != "excel":
        payload = get_data(
            network, sts, ets, stations, cols, na, query.format
        ).encode(
            "ascii",
            errors="ignore",
        )
        start_response("200 OK", [("Content-type", "text/plain")])
        return [payload]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=daily.xlsx"),
    ]
    payload = get_data(network, sts, ets, stations, cols, na, query.format)
    start_response("200 OK", headers)
    return [payload]
