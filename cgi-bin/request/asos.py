"""
Download interface for ASOS/AWOS data from the asos database
"""
import time
import os
import sys
from io import StringIO
import datetime

import pytz
from paste.request import parse_formvars
from pyiem.util import get_dbconn

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
    if val < 0.009999 and val > 0:
        return trace
    return "%.2f" % (val,)


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
    return "%.2f" % (val,)


def dance(val):
    """Force the val to ASCII."""
    return val.encode("ascii", "ignore").decode("ascii")


def check_load():
    """Prevent automation from overwhelming the server"""

    for i in range(5):
        pgconn = get_dbconn("mesosite")
        mcursor = pgconn.cursor()
        mcursor.execute(
            """
        select pid from pg_stat_activity where query ~* 'FETCH'
        and datname = 'asos'"""
        )
        if mcursor.rowcount < 30:
            return True
        pgconn.close()
        if i == 4:
            sys.stderr.write(
                (
                    "[client: %s] "
                    "/cgi-bin/request/asos.py over capacity: %s\n"
                )
                % (os.environ.get("REMOTE_ADDR"), mcursor.rowcount)
            )
        else:
            time.sleep(3)
    return False


def get_stations(form):
    """ Figure out the requested station """
    if "station" not in form:
        return []
    stations = form.getall("station")
    if not stations:
        return []
    # allow folks to specify the ICAO codes for K*** sites
    for i, station in enumerate(stations):
        if len(station) == 4 and station[0] == "K":
            stations[i] = station[1:]
    return stations


def get_time_bounds(form, tzinfo):
    """ Figure out the exact time bounds desired """
    # Here lie dragons, so tricky to get a proper timestamp
    try:
        y1 = int(form.get("year1"))
        y2 = int(form.get("year2"))
        m1 = int(form.get("month1"))
        m2 = int(form.get("month2"))
        d1 = int(form.get("day1"))
        d2 = int(form.get("day2"))
        sts = tzinfo.localize(datetime.datetime(y1, m1, d1))
        ets = tzinfo.localize(datetime.datetime(y2, m2, d2))
    except Exception:
        return None, None

    if sts == ets:
        ets += datetime.timedelta(days=1)
    return sts, ets


def build_querycols(form):
    """Which database columns correspond to our query."""
    req = form.getall("data")
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


def build_gisextra(form, dbstations, rD):
    """Build lookup table."""
    if form.get("latlon", "no") != "yes":
        return {}
    res = {}
    mesosite = get_dbconn("mesosite")
    mcursor = mesosite.cursor()
    mcursor.execute(
        """
        SELECT id, ST_x(geom) as lon, ST_y(geom) as lat
        from stations WHERE id in %s
        and (network ~* 'AWOS' or network ~* 'ASOS')
    """,
        (tuple(dbstations),),
    )
    for row in mcursor:
        res[row[0]] = "%.4f%s%.4f%s" % (row[1], rD, row[2], rD)
    mesosite.close()
    return res


def application(environ, start_response):
    """ Go main Go """
    if environ["REQUEST_METHOD"] == "OPTIONS":
        start_response("400 Bad Request", [("Content-type", "text/plain")])
        yield b"Allow: GET,POST,OPTIONS"
        return
    form = parse_formvars(environ)
    if not check_load():
        start_response(
            "503 Service Unavailable", [("Content-type", "text/plain")]
        )
        yield b"ERROR: server over capacity, please try later"
        return
    try:
        tzinfo = pytz.timezone(form.get("tz", "Etc/UTC"))
    except pytz.exceptions.UnknownTimeZoneError as exp:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        sys.stderr.write("asos.py invalid tz: %s\n" % (exp,))
        yield b"Invalid Timezone (tz) provided"
        return
    pgconn = get_dbconn("asos")
    acursor = pgconn.cursor("mystream")

    # Save direct to disk or view in browser
    direct = form.get("direct", "no") == "yes"
    report_type = form.getall("report_type")
    stations = get_stations(form)
    if not stations:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        yield b"No stations provided."
        return
    sts, ets = get_time_bounds(form, tzinfo)
    if sts is None:
        start_response(
            "500 Internal Server Error", [("Content-type", "text/plain")]
        )
        yield b"Invalid times provided."
        return
    headers = []
    if direct:
        headers.append(("Content-type", "application/octet-stream"))
        fn = "%s.txt" % (stations[0],)
        if len(stations) > 1:
            fn = "asos.txt"
        headers.append(
            ("Content-Disposition", "attachment; filename=%s" % (fn,))
        )
    else:
        headers.append(("Content-type", "text/plain"))
    start_response("200 OK", headers)

    dbstations = stations
    if len(dbstations) == 1:
        dbstations.append("XYZXYZ")

    delim = form.get("format", "onlycomma")
    # How should null values be represented
    missing = NULLS.get(form.get("missing"), "M")
    # How should trace values be represented
    trace = TRACE_OPTS.get(form.get("trace"), "0.0001")

    querycols = build_querycols(form)

    if delim in ["tdf", "onlytdf"]:
        rD = "\t"
    else:
        rD = ","

    gtxt = build_gisextra(form, dbstations, rD)
    gisextra = form.get("latlon", "no") == "yes"

    rlimiter = ""
    if len(report_type) == 1:
        rlimiter = " and report_type = %s" % (int(report_type[0]),)
    elif len(report_type) > 1:
        rlimiter = (" and report_type in %s") % (
            tuple([int(a) for a in report_type]),
        )
    sqlcols = ",".join(querycols)
    acursor.execute(
        """
        SELECT station, valid, """
        + sqlcols
        + """ from alldata
        WHERE valid >= %s and valid < %s and station in %s """
        + rlimiter
        + """
        ORDER by valid ASC
    """,
        (sts, ets, tuple(dbstations)),
    )

    sio = StringIO()
    if delim not in ["onlytdf", "onlycomma"]:
        sio.write("#DEBUG: Format Typ    -> %s\n" % (delim,))
        sio.write("#DEBUG: Time Period   -> %s %s\n" % (sts, ets))
        sio.write("#DEBUG: Time Zone     -> %s\n" % (tzinfo,))
        sio.write(
            (
                "#DEBUG: Data Contact   -> daryl herzmann "
                "akrherz@iastate.edu 515-294-5978\n"
            )
        )
        sio.write("#DEBUG: Entries Found -> %s\n" % (acursor.rowcount,))
    sio.write("station" + rD + "valid" + rD)
    if gisextra:
        sio.write("lon%slat%s" % (rD, rD))
    # hack to convert tmpf as tmpc to tmpc
    sio.write("%s\n" % (rD.join([c.split(" as ")[-1] for c in querycols]),))

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
    }
    # The default is the %.2f formatter
    formatters = [ff.get(col, fmt_f2) for col in querycols]

    gismiss = "%s%s%s%s" % (missing, rD, missing, rD)
    for rownum, row in enumerate(acursor):
        sio.write(row[0] + rD)
        sio.write((row[1].astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M") + rD)
        if gisextra:
            sio.write(gtxt.get(row[0], gismiss))
        sio.write(
            rD.join(
                [
                    func(val, missing, trace, tzinfo)
                    for func, val in zip(formatters, row[2:])
                ]
            )
            + "\n"
        )
        if rownum > 0 and rownum % 1000 == 0:
            yield sio.getvalue().encode("ascii", "ignore")
            sio = StringIO()
    yield sio.getvalue().encode("ascii", "ignore")
