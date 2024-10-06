""".. title:: ASOS/METAR Backend Service

Return to `API Mainpage </api/#cgi>`_ or the
`Download Portal </request/download.phtml>`_.

Documentation on /cgi-bin/request/asos.py
-----------------------------------------

This cgi-bin script provides METAR/ASOS data.  It has a IP-based rate limit for
requests to prevent abuse.  A `503 Service Unavailable` response will be
returned if the server is under heavy load.

Changelog:

- **2024-04-01** Fix recently introduced bug with time sort order.
- **2024-03-29** This service had an intermediate bug whereby if the `tz` value
  was not provided, it would default to `America/Chicago` instead of `UTC`.
- **2024-03-29** Migrated to pydantic based request validation.  Will be
  monitoring for any issues.
- **2024-03-14** Initial documentation release.

Example Usage
-------------

Get the past 24 hours of air temperature and dew point for Des Moines and
Mason City, Iowa.

https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py\
?data=tmpf&data=dwpf&station=DSM&station=MCW&hours=24

"""

import re
import sys
from datetime import datetime, timedelta
from io import StringIO
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AwareDatetime, Field, field_validator
from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.util import utc
from pyiem.webutil import CGIModel, ListOrCSVType, iemapp

STATION_RE = re.compile(r"^[A-Z0-9_]{3,4}$")
NULLS = {"M": "M", "null": "null", "empty": ""}
TRACE_OPTS = {"T": "T", "null": "null", "empty": "", "0.0001": "0.0001"}
AVAILABLE = [
    "tmpf",
    "dwpf",
    "relh",
    "drct",
    "sknt",
    "p01i",
    "alti",
    "mslp",
    "vsby",
    "gust",
    "skyc1",
    "skyc2",
    "skyc3",
    "skyc4",
    "skyl1",
    "skyl2",
    "skyl3",
    "skyl4",
    "wxcodes",
    "ice_accretion_1hr",
    "ice_accretion_3hr",
    "ice_accretion_6hr",
    "peak_wind_gust",
    "peak_wind_drct",
    "peak_wind_time",
    "feel",
    "metar",
    "snowdepth",
]
# inline is so much faster!
CONV_COLS = {
    "tmpc": "f2c(tmpf) as tmpc",
    "dwpc": "f2c(dwpf) as dwpc",
    "p01m": "p01i * 25.4 as p01m",
    "sped": "sknt * 1.15 as sped",
    "gust_mph": "gust * 1.15 as gust_mph",
    "peak_wind_gust_mph": "peak_wind_gust * 1.15 as peak_wind_gust_mph",
}


class MyModel(CGIModel):
    """Request Model."""

    data: ListOrCSVType = Field(
        None,
        description=(
            "The data columns to return, defaults to all.  The available "
            "options are: tmpf, dwpf, relh, drct, sknt, p01i, alti, mslp, "
            "vsby, gust, skyc1, skyc2, skyc3, skyc4, skyl1, skyl2, skyl3, "
            "skyl4, wxcodes, ice_accretion_1hr, ice_accretion_3hr, "
            "ice_accretion_6hr, peak_wind_gust, peak_wind_drct, "
            "peak_wind_time, feel, metar, snowdepth"
        ),
    )
    direct: bool = Field(
        False,
        description=(
            "If set to 'yes', the data will be directly downloaded as a file."
        ),
    )
    elev: bool = Field(
        False,
        description=(
            "If set to 'yes', the elevation (m) of the station will be "
            "included in the output."
        ),
    )
    ets: AwareDatetime = Field(
        None,
        description=("The end time of the data request."),
    )
    format: str = Field(
        "onlycomma",
        description=(
            "The format of the data, defaults to onlycomma.  The available "
            "options are: onlycomma, tdf."
        ),
    )
    hours: int = Field(
        None,
        description=(
            "The number of hours of data to return prior to the current "
            "timestamp.  Can not be more than 24 if no stations are specified."
        ),
    )
    latlon: bool = Field(
        False,
        description=(
            "If set to 'yes', the latitude and longitude of the station will "
            "be included in the output."
        ),
    )
    missing: str = Field(
        "M",
        description=(
            "How to represent missing values, defaults to M.  Other options "
            "are 'null' and 'empty'."
        ),
        pattern="^(M|null|empty)$",
    )
    nometa: bool = Field(
        False,
        description=(
            "If set to 'yes', the column headers will not be included in the "
            "output."
        ),
    )
    network: ListOrCSVType = Field(
        None,
        description="The network to query, defaults to all networks.",
    )
    report_type: ListOrCSVType = Field(
        [],
        description=(
            "The report type to query, defaults to all.  The available "
            "options are: 1 (HFMETAR), 3 (Routine), 4 (Specials)."
        ),
    )
    station: ListOrCSVType = Field(
        None,
        description=(
            "The station identifier to query, defaults to all stations and "
            "if you do not specify any stations, you can only request 24 "
            "hours of data."
        ),
    )
    sts: AwareDatetime = Field(
        None,
        description=("The start time of the data request."),
    )
    trace: str = Field(
        "0.0001",
        description=(
            "How to represent trace values, defaults to 0.0001.  Other "
            "options are 'null' and 'empty'."
        ),
        pattern="^(0.0001|null|empty|T)$",
    )
    tz: str = Field(
        "UTC",
        description=(
            "The timezone to use for the request timestamps (when not "
            "providing already tz-aware ``sts`` and ``ets`` values) and the "
            "output valid timestamp.  It is highly recommended to set this to "
            "UTC to ensure it is set.  This string should be "
            "something that the Python ``zoneinfo`` library can understand."
        ),
    )
    year1: int = Field(
        None,
        description=(
            "The year of the start time, defaults to the time zone provided "
            "by `tzname`. If `sts` is not provided."
        ),
    )
    month1: int = Field(
        None,
        description=(
            "The month of the start time, defaults to the time zone provided "
            "by `tzname`. If `sts` is not provided."
        ),
    )
    day1: int = Field(
        None,
        description=(
            "The day of the start time, defaults to the time zone provided by "
            "`tzname`. If `sts` is not provided."
        ),
    )
    hour1: int = Field(
        0,
        description=(
            "The hour of the start time, defaults to the time zone provided "
            "by `tzname`. If `sts` is not provided."
        ),
    )
    minute1: int = Field(
        0,
        description=(
            "The minute of the start time, defaults to the time zone provided "
            "by `tzname`. If `sts` is not provided."
        ),
    )
    year2: int = Field(
        None,
        description=(
            "The year of the end time, defaults to the time zone provided by "
            "`tzname`. If `ets` is not provided."
        ),
    )
    month2: int = Field(
        None,
        description=(
            "The month of the end time, defaults to the time zone provided by "
            "`tzname`. If `ets` is not provided."
        ),
    )
    day2: int = Field(
        None,
        description=(
            "The day of the end time, defaults to the time zone provided by "
            "`tzname`. If `ets` is not provided."
        ),
    )
    hour2: int = Field(
        0,
        description=(
            "The hour of the end time, defaults to the time zone provided by "
            "`tzname`. If `ets` is not provided."
        ),
    )
    minute2: int = Field(
        0,
        description=(
            "The minute of the end time, defaults to the time zone provided "
            "by `tzname`. If `ets` is not provided."
        ),
    )

    @field_validator("tz")
    @classmethod
    def valid_tz(cls, value):
        """Ensure the timezone is valid."""
        if value in ["", "etc/utc"]:
            return "UTC"
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exp:
            raise ValueError(f"Unknown timezone: {value}") from exp
        return value

    @field_validator("station")
    @classmethod
    def station_validator(cls, value):
        """Ensure the station is valid."""
        for station in value:
            if not STATION_RE.fullmatch(station):
                raise ValueError(f"Invalid station identifier: {station}")
        return value


def fmt_time(val, missing, _trace, tzinfo):
    """Format timestamp."""
    if val is None:
        return missing
    return (val.astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M")


def fmt_trace(val, missing, trace, _tzinfo):
    """Format precip."""
    if val is None:
        return missing
    # careful with this comparison
    if 0 < val < 0.009999:
        return trace
    return f"{val:.2f}"


def fmt_simple(val, missing, _trace, _tzinfo):
    """Format simplely."""
    if val is None:
        return missing
    return dance(val).replace(",", " ").replace("\n", " ")


def fmt_wxcodes(val, missing, _trace, _tzinfo):
    """Format weather codes."""
    if val is None:
        return missing
    return " ".join(val)


def fmt_f2(val, missing, _trace, _tzinfo):
    """Simple 2 place formatter."""
    if val is None:
        return missing
    return f"{val:.2f}"


def fmt_f0(val, missing, _trace, _tzinfo):
    """Simple 0 place formatter."""
    if val is None:
        return missing
    return f"{val:.0f}"


def dance(val):
    """Force the val to ASCII."""
    return val.encode("ascii", "ignore").decode("ascii")


def overloaded():
    """Prevent automation from overwhelming the server"""

    with get_dbconn("asos") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute("select one::float from system_loadavg")
        val = cursor.fetchone()[0]
    if val > 30:  # Cut back on logging
        sys.stderr.write(f"/cgi-bin/request/asos.py over cpu thres: {val}\n")
    return val > 20


def get_stations(form):
    """Figure out the requested station"""
    if not form["station"]:
        if form["network"] is not None:
            nt = NetworkTable(form["network"], only_online=False)
            return list(nt.sts.keys())
        return []
    stations = form["station"]
    if not stations:
        return []
    # allow folks to specify the ICAO codes for K*** sites
    for i, station in enumerate(stations):
        if len(station) == 4 and station[0] == "K":
            stations[i] = station[1:]
    return stations


def get_time_bounds(form, tzinfo):
    """Figure out the exact time bounds desired"""
    if form["hours"] is not None:
        ets = utc()
        sts = ets - timedelta(hours=int(form.get("hours")))
        return sts, ets
    # Here lie dragons, so tricky to get a proper timestamp
    try:

        def _get(num):
            return datetime(
                form[f"year{num}"],
                form[f"month{num}"],
                form[f"day{num}"],
                form[f"hour{num}"],
                form[f"minute{num}"],
            )

        if form["sts"] is None:
            form["sts"] = _get("1").replace(tzinfo=tzinfo)
        if form["ets"] is None:
            form["ets"] = _get("2").replace(tzinfo=tzinfo)
    except Exception:
        return None, None

    if form["sts"] == form["ets"]:
        form["ets"] += timedelta(days=1)
    if form["sts"] > form["ets"]:
        form["sts"], form["ets"] = form["ets"], form["sts"]
    return form["sts"], form["ets"]


def build_querycols(form):
    """Which database columns correspond to our query."""
    req = form["data"]
    if not req or "all" in req:
        return AVAILABLE
    res = []
    for col in req:
        if col == "presentwx":
            res.append("wxcodes")
        elif col in AVAILABLE:
            res.append(col)
        elif col in CONV_COLS:
            res.append(CONV_COLS[col])
    if not res:
        res.append("tmpf")
    return res


def toobusy(pgconn, name):
    """Check internal logging..."""
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT pid from pg_stat_activity where query ~* %s",
        (name,),
    )
    over = cursor.rowcount > 6
    if over and cursor.rowcount > 9:  # cut back on logging
        sys.stderr.write(f"asos.py cursors {cursor.rowcount}: {name}\n")
    cursor.close()
    return over


@iemapp(help=__doc__, parse_times=False, schema=MyModel)
def application(environ, start_response):
    """Go main"""
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        yield b"Allow: GET,POST,OPTIONS"
        return
    if overloaded():
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        yield b"ERROR: server over capacity, please try later"
        return
    tzinfo = ZoneInfo(environ["tz"])
    pgconn = get_dbconn("asos")
    ip = (
        environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR"))
        .split(",")[0]
        .strip()
    )
    cursor_name = f"mystream_{ip}"
    if toobusy(pgconn, cursor_name):
        pgconn.close()
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        yield b"ERROR: server over capacity, please try later"
        return
    acursor = pgconn.cursor(cursor_name, scrollable=False)
    acursor.itersize = 2000

    report_types = [int(i) for i in environ["report_type"]]
    sts, ets = get_time_bounds(environ, tzinfo)
    if sts is None:
        pgconn.close()
        start_response(
            "422 Unprocessable Entity", [("Content-type", "text/plain")]
        )
        yield b"Invalid times provided."
        return
    stations = get_stations(environ)
    if not stations:
        # We are asking for all-data.  We limit the amount of data returned to
        # one day or less
        if (ets - sts) > timedelta(hours=24):
            pgconn.close()
            start_response("400 Bad Request", [("Content-type", "text/plain")])
            yield b"When requesting all-stations, must be less than 24 hours."
            return
    delim = environ["format"]
    headers = []
    if environ["direct"]:
        headers.append(("Content-type", "application/octet-stream"))
        suffix = "tsv" if delim in ["tdf", "onlytdf"] else "csv"
        if not stations or len(stations) > 1:
            fn = f"asos.{suffix}"
        else:
            fn = f"{stations[0]}.{suffix}"
        headers.append(("Content-Disposition", f"attachment; filename={fn}"))
    else:
        headers.append(("Content-type", "text/plain"))
    start_response("200 OK", headers)

    # How should null values be represented
    missing = NULLS[environ["missing"]]
    # How should trace values be represented
    trace = TRACE_OPTS[environ["trace"]]

    querycols = build_querycols(environ)

    if delim in ["tdf", "onlytdf"]:
        rD = "\t"
    else:
        rD = ","

    gisextra = environ["latlon"]
    elev_extra = environ["elev"]
    table = "alldata"
    metalimiter = ""
    colextra = "0 as lon, 0 as lat, 0 as elev, "
    if gisextra or elev_extra:
        colextra = "ST_X(geom) as lon, ST_Y(geom) as lat, elevation, "
        table = "alldata a JOIN stations t on (a.station = t.id)"
        metalimiter = "t.network ~* 'ASOS' and "

    rlimiter = ""
    # Munge legacy report_type=2 into 2,3,4 see akrherz/iem#104
    if 2 in report_types:
        report_types.extend([3, 4])
    if len(report_types) == 1:
        rlimiter = f" and report_type = {report_types[0]}"
    elif len(report_types) > 1:
        rlimiter = f" and report_type in {tuple(report_types)}"
    sqlcols = ",".join(querycols)
    sorder = "DESC" if environ["hours"] is not None else "ASC"
    if stations:
        acursor.execute(
            f"SELECT station, valid, {colextra} {sqlcols} from {table} "
            f"WHERE {metalimiter} valid >= %s and valid < %s and "
            f"station = ANY(%s) {rlimiter} ORDER by valid {sorder}",
            (sts, ets, stations),
        )
    else:
        acursor.execute(
            f"SELECT station, valid, {colextra} {sqlcols} from {table} "
            f"WHERE {metalimiter} valid >= %s and valid < %s {rlimiter} "
            f"ORDER by valid {sorder}",
            (sts, ets),
        )
    sio = StringIO()
    if delim not in ["onlytdf", "onlycomma"]:
        sio.write(f"#DEBUG: Format Typ    -> {delim}\n")
        sio.write(f"#DEBUG: Time Period   -> {sts} {ets}\n")
        sio.write(f"#DEBUG: Time Zone     -> {tzinfo}\n")
        sio.write(
            "#DEBUG: Data Contact   -> daryl herzmann "
            "akrherz@iastate.edu 515-294-5978\n"
        )
        sio.write(f"#DEBUG: Entries Found -> {acursor.rowcount}\n")
    nometa = environ["nometa"]
    if not nometa:
        sio.write(f"station{rD}valid{rD}")
        if gisextra:
            sio.write(f"lon{rD}lat{rD}")
        if elev_extra:
            sio.write(f"elevation{rD}")
        # hack to convert tmpf as tmpc to tmpc
        sio.write(
            f"{rD.join([c.rsplit(' as ', maxsplit=1)[-1] for c in querycols])}"
        )
        sio.write("\n")

    ff = {
        "wxcodes": fmt_wxcodes,
        "metar": fmt_simple,
        "skyc1": fmt_simple,
        "skyc2": fmt_simple,
        "skyc3": fmt_simple,
        "skyc4": fmt_simple,
        "p01i": fmt_trace,
        "p01i * 25.4 as p01m": fmt_trace,
        "ice_accretion_1hr": fmt_trace,
        "ice_accretion_3hr": fmt_trace,
        "ice_accretion_6hr": fmt_trace,
        "peak_wind_time": fmt_time,
        "snowdepth": fmt_f0,
    }
    # The default is the %.2f formatter
    formatters = [ff.get(col, fmt_f2) for col in querycols]

    for rownum, row in enumerate(acursor):
        if not nometa:
            sio.write(row[0] + rD)
            sio.write(
                (row[1].astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M") + rD
            )
        if gisextra:
            sio.write(f"{row[2]:.4f}{rD}{row[3]:.4f}{rD}")
        if elev_extra:
            sio.write(f"{row[4]:.2f}{rD}")
        sio.write(
            rD.join(
                [
                    func(val, missing, trace, tzinfo)
                    for func, val in zip(formatters, row[5:])
                ]
            )
            + "\n"
        )
        if rownum > 0 and rownum % 1000 == 0:
            yield sio.getvalue().encode("ascii", "ignore")
            sio = StringIO()
    acursor.close()
    pgconn.close()
    yield sio.getvalue().encode("ascii", "ignore")
