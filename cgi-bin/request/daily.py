""".. title:: IEM Computed Daily Summaries

Documentation for /cgi-bin/request/daily.py
-------------------------------------------

This data source contains a combination of IEM computed calendar day summaries
and some more official totals with some sites reporting explicit values.  One
should also note that typically the airport stations are for a 24 hour period
over standard time, which means 1 AM to 1 AM daylight time.

Example Usage
-------------

Request all high temperature data for Ames, IA (AMW) for the month of January
2019:

    https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?sts=2019-01-01&ets=2019-01-31&network=IA_ASOS&stations=AMW&var=max_temp_f&format=csv


Request daily precipitation and the climatology for all stations in Washington
state on 23 June 2023 in Excel format:

    https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?sts=2023-06-23&ets=2023-06-23&network=WA_ASOS&stations=_ALL&var=precip_in,climo_precip_in&format=excel

"""

import copy
import sys
from datetime import datetime
from io import BytesIO, StringIO

import pandas as pd
from pydantic import Field
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.exceptions import IncompleteWebRequest
from pyiem.network import Table as NetworkTable
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp
from sqlalchemy import text

EXL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
DEFAULT_COLS = (
    "max_temp_f,min_temp_f,max_dewpoint_f,min_dewpoint_f,precip_in,"
    "avg_wind_speed_kts,avg_wind_drct,min_rh,avg_rh,max_rh,"
    "climo_high_f,climo_low_f,climo_precip_in,snow_in,snowd_in,"
    "min_feel,avg_feel,max_feel,max_wind_speed_kts,max_wind_gust_kts,"
    "srad_mj"
).split(",")


class MyCGI(CGIModel):
    ets: datetime = Field(None, description="End date to query")
    format: str = Field("csv", description="The format of the output")
    na: str = Field("None", description="The NA value to use")
    network: str = Field(..., description="Network Identifier")
    station: ListOrCSVType = Field(
        [],
        description=(
            "Comma delimited or multi-param station identifiers, "
            "_ALL for all stations in network (deprecated)"
        ),
    )
    stations: ListOrCSVType = Field(
        [],
        description=(
            "Comma delimited or multi-param station identifiers, "
            "_ALL for all stations in network"
        ),
    )
    sts: datetime = Field(None, description="Start date to query")
    var: ListOrCSVType = Field(
        None,
        description=(
            "Comma delimited or multi-param variable names to include in "
            f"output, columns are: {DEFAULT_COLS}"
        ),
    )
    year1: int = Field(None, description="Start year when sts is not provided")
    month1: int = Field(
        None, description="Start month when sts is not provided"
    )
    day1: int = Field(None, description="Start day when sts is not provided")
    year2: int = Field(None, description="End year when ets is not provided")
    month2: int = Field(None, description="End month when ets is not provided")
    day2: int = Field(None, description="End day when ets is not provided")


def overloaded():
    """Prevent automation from overwhelming the server"""

    with get_dbconn("iem") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute("select one::float from system_loadavg")
        val = cursor.fetchone()[0]
    if val > 25:  # Cut back on logging
        sys.stderr.write(f"/cgi-bin/request/daily.py over cpu thres: {val}\n")
    return val > 20


def get_climate(network, stations):
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
            text(
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


def get_data(network, sts, ets, stations, cols, na, fmt):
    """Go fetch data please"""
    if not cols:
        cols = copy.deepcopy(DEFAULT_COLS)
    cols.insert(0, "day")
    cols.insert(0, "station")
    climate = get_climate(network, stations)
    if isinstance(climate, str):
        return climate

    with get_sqlalchemy_conn("iem") as conn:
        df = pd.read_sql(
            text(
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
            srad_mj, ncei91, to_char(day, 'mmdd') as sday
            from summary s JOIN stations t
            on (t.iemid = s.iemid) WHERE
            s.day >= :st and s.day <= :et and
            t.network = :n and t.id = ANY(:ds)
            ORDER by day ASC"""
            ),
            conn,
            params={"st": sts, "et": ets, "n": network, "ds": stations},
        )
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
        return df.to_json(orient="records")
    if fmt == "excel":
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Data", index=False)
        return bio.getvalue()

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@iemapp(help=__doc__, schema=MyCGI, parse_times=True)
def application(environ, start_response):
    """See how we are called"""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Missing start and end times")
    sts, ets = environ["sts"].date(), environ["ets"].date()

    if sts.year != ets.year and overloaded():
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        return [b"ERROR: server over capacity, please try later"]

    fmt = environ.get("format", "csv")
    stations = environ["stations"]
    if not stations:
        stations = environ["station"]
    if not stations:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: No stations specified for request"]
    network = environ["network"][:20]
    if "_ALL" in stations:
        if (ets - sts).days > 366:
            raise IncompleteWebRequest(
                "Must request a year or less when requesting all stations"
            )
        stations = list(NetworkTable(network, only_online=False).sts.keys())
    cols = environ["var"]
    na = environ["na"]
    if na not in ["M", "None", "blank"]:
        start_response("200 OK", [("Content-type", "text/plain")])
        return [b"ERROR: Invalid `na` value provided. {M, None, blank}"]
    if fmt != "excel":
        start_response("200 OK", [("Content-type", "text/plain")])
        return [
            get_data(network, sts, ets, stations, cols, na, fmt).encode(
                "ascii"
            )
        ]
    headers = [
        ("Content-type", EXL),
        ("Content-disposition", "attachment; Filename=daily.xlsx"),
    ]
    start_response("200 OK", headers)
    return [get_data(network, sts, ets, stations, cols, na, fmt)]
