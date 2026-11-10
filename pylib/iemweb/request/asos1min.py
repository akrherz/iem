""".. title:: ASOS 1 Minute Data Request

Documentation for /cgi-bin/request/asos1min.py
----------------------------------------------

This service provides the ASOS 1 minute data provided by NCEI and is not the
"one minute data" via MADIS.  There is an availability delay of about 24 hours
due to the way NCEI collects the data from the ASOS sites.

Examples
--------

Request air temperature data for Ames IA KAMW for 2022, but only provide data
at 1 hour intervals.  Provide timestamps in UTC timezone.

https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py?station=AMW\
&vars=tmpf&sts=2022-01-01T00:00Z&ets=2023-01-01T00:00Z&sample=1hour\
&what=download&tz=UTC

"""

from io import StringIO
from typing import Annotated

from pydantic import AwareDatetime, Field
from pyiem.database import get_sqlalchemy_conn, sql_helper
from pyiem.exceptions import IncompleteWebRequest
from pyiem.web.fields import (
    DAY_OF_MONTH_FIELD_OPTIONAL,
    HOUR_FIELD,
    MINUTE_FIELD,
    MONTH_FIELD_OPTIONAL,
    STATION_LIST_FIELD,
    TZ_FIELD,
    YEAR_FIELD_OPTIONAL,
)
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

SAMPLING = {
    "1min": 1,
    "5min": 5,
    "10min": 10,
    "20min": 20,
    "1hour": 60,
}
DELIM = {"space": " ", "comma": ",", "tab": "\t", ",": ","}


class Schema(CGIModel):
    """See how we are called."""

    delim: Annotated[
        str,
        Field(
            description="Delimiter to use in output",
            pattern="^(comma|space|tab|,)$",
        ),
    ] = "comma"
    ets: Annotated[
        AwareDatetime | None, Field(description="End timestamp for data")
    ] = None
    gis: Annotated[
        bool, Field(description="Include Lat/Lon information in output")
    ] = False
    sample: Annotated[
        str,
        Field(
            description="Sampling period for data",
            pattern="^(1min|5min|10min|20min|1hour)$",
        ),
    ] = "1min"
    station: STATION_LIST_FIELD
    sts: Annotated[
        AwareDatetime | None, Field(description="Start timestamp for data")
    ] = None
    tz: TZ_FIELD = "UTC"
    vars: Annotated[
        ListOrCSVType | None,
        Field(description="Variable(s) to request data for"),
    ] = None
    what: Annotated[
        str,
        Field(description="Output format", pattern="^(download|view)$"),
    ] = "dl"
    year1: YEAR_FIELD_OPTIONAL = None
    month1: MONTH_FIELD_OPTIONAL = None
    day1: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour1: HOUR_FIELD = 0
    minute1: MINUTE_FIELD = 0
    year2: YEAR_FIELD_OPTIONAL = None
    month2: MONTH_FIELD_OPTIONAL = None
    day2: DAY_OF_MONTH_FIELD_OPTIONAL = None
    hour2: HOUR_FIELD = 0
    minute2: MINUTE_FIELD = 0


def get_station_metadata(stations) -> dict:
    """build a dictionary."""
    with get_sqlalchemy_conn("mesosite") as conn:
        res = conn.execute(
            sql_helper("""
            SELECT id, name, round(ST_x(geom)::numeric, 4) as lon,
            round(ST_y(geom)::numeric, 4) as lat from stations
            where id = ANY(:stations) and network ~* 'ASOS'
        """),
            {"stations": stations},
        )
        data = {}
        for row in res.mappings():
            data[row["id"]] = dict(
                name=row["name"], lon=row["lon"], lat=row["lat"]
            )
    for station in stations:
        if station not in data:
            raise IncompleteWebRequest(f"Unknown station provided: {station}")
    return data


def compute_prefixes(sio, environ, delim, stations, tz) -> dict:
    """"""
    station_meta = get_station_metadata(stations)
    prefixes = {}
    if environ["gis"]:
        sio.write(
            delim.join(
                ["station", "station_name", "lat", "lon", f"valid({tz})", ""]
            )
        )
        for station in stations:
            prefixes[station] = (
                delim.join(
                    [
                        station,
                        station_meta[station]["name"].replace(delim, "_"),
                        str(station_meta[station]["lat"]),
                        str(station_meta[station]["lon"]),
                    ]
                )
                + delim
            )
    else:
        sio.write(delim.join(["station", "station_name", f"valid({tz})", ""]))
        for station in stations:
            prefixes[station] = (
                delim.join(
                    [
                        station,
                        station_meta[station]["name"].replace(delim, "_"),
                    ]
                )
                + delim
            )
    return prefixes


@iemapp(
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Handle mod_wsgi request."""
    if environ["sts"] is None or environ["ets"] is None:
        raise IncompleteWebRequest("Insufficient start timestamp variables.")
    # Ensure we have uppercase stations
    stations = [s.upper() for s in environ["station"]]
    delim = DELIM[environ["delim"]]
    sample = SAMPLING[environ["sample"]]
    tz = environ["tz"]
    varnames = environ["vars"]
    if not varnames:
        raise IncompleteWebRequest("No vars= was specified in request.")
    with get_sqlalchemy_conn("asos1min") as conn:
        # get a list of columns we have in the alldata_1minute table
        res = conn.execute(
            sql_helper(
                "select column_name from information_schema.columns where "
                "table_name = 'alldata_1minute' ORDER by column_name"
            )
        )
        columns = [row["column_name"] for row in res.mappings()]
        # cross check varnames now
        for varname in varnames:
            if varname not in columns:
                raise IncompleteWebRequest(
                    f"Unknown variable {varname} specified in request."
                )
        res = conn.execution_options(
            stream_results=True, max_row_buffer=10_000
        ).execute(
            sql_helper("""
    select *,
    to_char(valid at time zone :tz, 'YYYY-MM-DD hh24:MI') as local_valid
    from alldata_1minute
    where station = ANY(:stations) and valid >= :sts and valid < :ets and
    extract(minute from valid) % :sample = 0 ORDER by station, valid
            """),
            {
                "tz": tz,
                "stations": stations,
                "sts": environ["sts"],
                "ets": environ["ets"],
                "sample": sample,
            },
        )
        headers = []
        if environ["what"] == "download":
            headers.append(("Content-type", "application/octet-stream"))
            headers.append(
                ("Content-Disposition", "attachment; filename=changeme.txt")
            )
        else:
            headers.append(("Content-type", "text/plain"))

        sio = StringIO()
        prefixes = compute_prefixes(sio, environ, delim, stations, tz)

        sio.write(delim.join(varnames) + "\n")
        rowfmt = delim.join([f"%({var})s" for var in varnames])
        for row in res.mappings():
            sio.write(prefixes[row["station"]])
            sio.write(f"{row['local_valid']}{delim}")
            sio.write((rowfmt % row).replace("None", "M"))
            sio.write("\n")

    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
