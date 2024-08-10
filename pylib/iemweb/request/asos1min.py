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
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, Field, field_validator
from pyiem.exceptions import IncompleteWebRequest
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

    delim: str = Field(
        "comma",
        description="Delimiter to use in output",
        pattern="^(comma|space|tab|,)$",
    )
    ets: AwareDatetime = Field(None, description="End timestamp for data")
    gis: bool = Field(
        False, description="Include Lat/Lon information in output"
    )
    sample: str = Field(
        "1min",
        description="Sampling period for data",
        pattern="^(1min|5min|10min|20min|1hour)$",
    )
    station: ListOrCSVType = Field(
        ..., description="Station(s) to request data for"
    )
    sts: AwareDatetime = Field(None, description="Start timestamp for data")
    tz: str = Field(
        "UTC",
        description="Timezone to use for the output and input timestamps",
    )
    vars: ListOrCSVType = Field(
        None, description="Variable(s) to request data for"
    )
    what: str = Field(
        "dl", description="Output format", pattern="^(download|view)$"
    )
    year1: int = Field(None, description="Start year for data")
    month1: int = Field(None, description="Start month for data")
    day1: int = Field(None, description="Start day for data")
    hour1: int = Field(0, description="Start hour for data")
    minute1: int = Field(0, description="Start minute for data")
    year2: int = Field(None, description="End year for data")
    month2: int = Field(None, description="End month for data")
    day2: int = Field(None, description="End day for data")
    hour2: int = Field(0, description="End hour for data")
    minute2: int = Field(0, description="End minute for data")

    @field_validator("tz")
    @classmethod
    def valid_tz(cls, value):
        """Ensure the timezone is valid."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exp:
            raise ValueError(f"Unknown timezone: {value}") from exp
        return value


def get_station_metadata(environ, stations) -> dict:
    """build a dictionary."""
    cursor = environ["iemdb.mesosite.cursor"]
    cursor.execute(
        """
        SELECT id, name, round(ST_x(geom)::numeric, 4) as lon,
        round(ST_y(geom)::numeric, 4) as lat from stations
        where id = ANY(%s) and network ~* 'ASOS'
    """,
        (stations,),
    )
    res = {}
    for row in cursor:
        res[row["id"]] = dict(name=row["name"], lon=row["lon"], lat=row["lat"])
    for station in stations:
        if station not in res:
            raise IncompleteWebRequest(f"Unknown station provided: {station}")
    return res


def compute_prefixes(sio, environ, delim, stations, tz) -> dict:
    """"""
    station_meta = get_station_metadata(environ, stations)
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
    iemdb=["asos1min", "mesosite"],
    iemdb_cursor="blah",
    help=__doc__,
    schema=Schema,
)
def application(environ, start_response):
    """Handle mod_wsgi request."""
    if environ["station"] is None:
        raise IncompleteWebRequest("No station= was specified in request.")
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
    cursor = environ["iemdb.asos1min.cursor"]
    # get a list of columns we have in the alldata_1minute table
    cursor.execute(
        "select column_name from information_schema.columns where "
        "table_name = 'alldata_1minute' ORDER by column_name"
    )
    columns = [row["column_name"] for row in cursor]
    # cross check varnames now
    for varname in varnames:
        if varname not in columns:
            raise IncompleteWebRequest(
                f"Unknown variable {varname} specified in request."
            )
    cursor.execute(
        """
        select *,
        to_char(valid at time zone %s, 'YYYY-MM-DD hh24:MI') as local_valid
        from alldata_1minute
        where station = ANY(%s) and valid >= %s and valid < %s and
        extract(minute from valid) %% %s = 0 ORDER by station, valid
        """,
        (tz, stations, environ["sts"], environ["ets"], sample),
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
    for row in cursor:
        sio.write(prefixes[row["station"]])
        sio.write(f"{row['local_valid']}{delim}")
        sio.write((rowfmt % row).replace("None", "M"))
        sio.write("\n")

    start_response("200 OK", headers)
    return [sio.getvalue().encode("ascii")]
