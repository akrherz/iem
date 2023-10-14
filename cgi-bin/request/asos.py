"""
Download interface for ASOS data from the asos database
"""
import datetime
import sys
from io import StringIO
from zoneinfo import ZoneInfo
from zoneinfo._common import ZoneInfoNotFoundError

from pyiem.network import Table as NetworkTable
from pyiem.util import get_dbconn, utc
from pyiem.webutil import iemapp

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
    if "station" not in form:
        if "network" in form:
            nt = NetworkTable(form.get("network"), only_online=False)
            return list(nt.sts.keys())
        return []
    stations = form.get("station")
    if not isinstance(stations, list):
        stations = [stations]
    if not stations:
        return []
    # allow folks to specify the ICAO codes for K*** sites
    for i, station in enumerate(stations):
        if len(station) == 4 and station[0] == "K":
            stations[i] = station[1:]
    return stations


def get_time_bounds(form, tzinfo):
    """Figure out the exact time bounds desired"""
    if "hours" in form:
        ets = utc()
        sts = ets - datetime.timedelta(hours=int(form.get("hours")))
        return sts, ets
    # Here lie dragons, so tricky to get a proper timestamp
    try:

        def _get(num):
            return datetime.datetime(
                int(form[f"year{num}"]),
                int(form[f"month{num}"]),
                int(form[f"day{num}"]),
                int(form.get(f"hour{num}", 0)),
                int(form.get(f"minute{num}", 0)),
            )

        sts = _get("1").replace(tzinfo=tzinfo)
        ets = _get("2").replace(tzinfo=tzinfo)
    except Exception:
        return None, None

    if sts == ets:
        ets += datetime.timedelta(days=1)
    if sts > ets:
        sts, ets = ets, sts
    return sts, ets


def build_querycols(form):
    """Which database columns correspond to our query."""
    req = form.get("data")
    if not isinstance(req, list):
        req = [req]
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


@iemapp()
def application(environ, start_response):
    """Go main Go"""
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
    try:
        tzname = environ.get("tz", "UTC").strip()
        if tzname in ["etc/utc", ""]:
            tzname = "UTC"
        tzinfo = ZoneInfo(tzname)
    except ZoneInfoNotFoundError as exp:
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        sys.stderr.write(f"asos.py invalid tz: {exp}\n")
        yield b"Invalid Timezone (tz) provided"
        return
    pgconn = get_dbconn("asos")
    cursor_name = f"mystream_{environ.get('REMOTE_ADDR')}"
    if toobusy(pgconn, cursor_name):
        pgconn.close()
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        yield b"ERROR: server over capacity, please try later"
        return
    acursor = pgconn.cursor(cursor_name, scrollable=False)
    acursor.itersize = 2000

    # Save direct to disk or view in browser
    direct = environ.get("direct", "no") == "yes"
    report_types = environ.get("report_type", [])
    if not isinstance(report_types, list):
        report_types = [report_types]
    report_types = [int(i) for i in report_types]
    sts, ets = get_time_bounds(environ, tzinfo)
    if sts is None:
        pgconn.close()
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        yield b"Invalid times provided."
        return
    stations = get_stations(environ)
    if not stations:
        # We are asking for all-data.  We limit the amount of data returned to
        # one day or less
        if (ets - sts) > datetime.timedelta(hours=24):
            pgconn.close()
            start_response("400 Bad Request", [("Content-type", "text/plain")])
            yield b"When requesting all-stations, must be less than 24 hours."
            return
    delim = environ.get("format", "onlycomma")
    headers = []
    if direct:
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
    missing = NULLS.get(environ.get("missing"), "M")
    # How should trace values be represented
    trace = TRACE_OPTS.get(environ.get("trace"), "0.0001")

    querycols = build_querycols(environ)

    if delim in ["tdf", "onlytdf"]:
        rD = "\t"
    else:
        rD = ","

    gisextra = environ.get("latlon", "no") == "yes"
    elev_extra = environ.get("elev", "no") == "yes"
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
    sorder = "DESC" if "hours" in environ else "ASC"
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
            (
                "#DEBUG: Data Contact   -> daryl herzmann "
                "akrherz@iastate.edu 515-294-5978\n"
            )
        )
        sio.write(f"#DEBUG: Entries Found -> {acursor.rowcount}\n")
    nometa = "nometa" in environ
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
    pgconn.close()
    yield sio.getvalue().encode("ascii", "ignore")
