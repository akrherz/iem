#!/usr/bin/env python
"""
Download interface for ASOS/AWOS data from the asos database
"""
import time
import cgi
import os
import sys
import datetime

import pytz
from metpy.units import units
from pyiem.util import get_dbconn, ssw

NULLS = {
    "M": "M",
    "null": "null",
    "empty": ""
}
TRACE_OPTS = {
    "T": "T",
    "null": "null",
    "empty": "",
    "0.0001": '0.0001'
}
AVAILABLE = [
    'tmpf',
    'dwpf',
    'relh',
    'drct',
    'sknt',
    'p01i',
    'alti',
    'mslp',
    'vsby',
    'gust',
    'skyc1',
    'skyc2',
    'skyc3',
    'skyc4',
    'skyl1',
    'skyl2',
    'skyl3',
    'skyl4',
    'wxcodes',
    'ice_accretion_1hr',
    'ice_accretion_3hr',
    'ice_accretion_6hr',
    'feel',
    'metar',
]
# inline is so much faster!
CONV_COLS = {
    'tmpc': 'f2c(tmpf) as tmpc',
    'dwpc': 'f2c(dwpf) as dwpc',
    'p01m': 'p01i * 25.4 as p01m',
    'sped': 'sknt * 1.15 as sped',
    'gust_mph': 'gust * 1.15 as gust_mph',
}
DEGC = units('degC')
DEGF = units('degF')


def fmt_trace(val, missing, trace):
    """Format precip."""
    if val is None:
        return missing
    # careful with this comparison
    if val < 0.009999 and val > 0:
        return trace
    return "%.2f" % (val, )


def fmt_simple(val, missing, _trace):
    """Format simplely."""
    if val is None:
        return missing
    return dance(val).replace(",", " ").replace("\n", " ")


def fmt_wxcodes(val, missing, _trace):
    """Format weather codes."""
    if val is None:
        return missing
    return " ".join(val)


def fmt_f2(val, missing, _trace):
    """Simple 2 place formatter."""
    if val is None:
        return missing
    return "%.2f" % (val, )


def dance(val):
    """Force the val to ASCII."""
    return val.encode('ascii', 'ignore').decode('ascii')


def check_load():
    """Prevent automation from overwhelming the server"""
    if os.environ['REQUEST_METHOD'] == 'OPTIONS':
        ssw("Allow: GET,POST,OPTIONS\n\n")
        sys.exit()
    for i in range(5):
        pgconn = get_dbconn('mesosite')
        mcursor = pgconn.cursor()
        mcursor.execute("""
        select pid from pg_stat_activity where query ~* 'FETCH'
        and datname = 'asos'""")
        if mcursor.rowcount < 30:
            return
        pgconn.close()
        if i == 4:
            sys.stderr.write(("[client: %s] "
                              "/cgi-bin/request/asos.py over capacity: %s\n"
                              ) % (os.environ.get('REMOTE_ADDR'),
                                   mcursor.rowcount))
        else:
            time.sleep(3)
    ssw("Content-type: text/plain \n")
    ssw('Status: 503 Service Unavailable\n\n')
    ssw("ERROR: server over capacity, please try later")
    sys.exit(0)


def get_stations(form):
    """ Figure out the requested station """
    if "station" not in form:
        ssw("Content-type: text/plain \n\n")
        ssw("ERROR: station must be specified!")
        sys.exit(0)
    stations = form.getlist("station")
    if not stations:
        ssw("Content-type: text/plain \n\n")
        ssw("ERROR: station must be specified!")
        sys.exit(0)
    # allow folks to specify the ICAO codes for K*** sites
    for i, station in enumerate(stations):
        if len(station) == 4 and station[0] == 'K':
            stations[i] = station[1:]
    return stations


def get_time_bounds(form, tzinfo):
    """ Figure out the exact time bounds desired """
    y1 = int(form.getfirst('year1'))
    y2 = int(form.getfirst('year2'))
    m1 = int(form.getfirst('month1'))
    m2 = int(form.getfirst('month2'))
    d1 = int(form.getfirst('day1'))
    d2 = int(form.getfirst('day2'))
    # Here lie dragons, so tricky to get a proper timestamp
    try:
        sts = tzinfo.localize(datetime.datetime(y1, m1, d1))
        ets = tzinfo.localize(datetime.datetime(y2, m2, d2))
    except Exception as exp:
        sys.stderr.write("asos.py malformed date: %s\n" % (exp, ))
        ssw("ERROR: Malformed Date!")
        sys.exit()

    if sts == ets:
        ets += datetime.timedelta(days=1)
    return sts, ets


def build_querycols(form):
    """Which database columns correspond to our query."""
    req = form.getlist("data")
    if not req or 'all' in req:
        return AVAILABLE
    res = []
    for col in req:
        if col == 'presentwx':
            res.append('wxcodes')
        elif col in AVAILABLE:
            res.append(col)
        elif col in CONV_COLS:
            res.append(CONV_COLS[col])
    if not res:
        res.append('tmpf')
    return res


def build_gisextra(form, dbstations, rD):
    """Build lookup table."""
    if form.getfirst("latlon", "no") != "yes":
        return {}
    res = {}
    mesosite = get_dbconn('mesosite')
    mcursor = mesosite.cursor()
    mcursor.execute("""
        SELECT id, ST_x(geom) as lon, ST_y(geom) as lat
        from stations WHERE id in %s
        and (network ~* 'AWOS' or network ~* 'ASOS')
    """, (tuple(dbstations),))
    for row in mcursor:
        res[row[0]] = "%.4f%s%.4f%s" % (row[1], rD, row[2], rD)
    mesosite.close()
    return res


def main():
    """ Go main Go """
    check_load()
    form = cgi.FieldStorage()
    try:
        tzinfo = pytz.timezone(form.getfirst("tz", "Etc/UTC"))
    except pytz.exceptions.UnknownTimeZoneError as exp:
        ssw("Content-type: text/plain\n\n")
        ssw("Invalid Timezone (tz) provided")
        sys.stderr.write("asos.py invalid tz: %s\n" % (exp, ))
        sys.exit()
    pgconn = get_dbconn('asos')
    acursor = pgconn.cursor('mystream')

    # Save direct to disk or view in browser
    direct = (form.getfirst('direct', 'no') == 'yes')
    report_type = form.getlist('report_type')
    stations = get_stations(form)
    if direct:
        ssw('Content-type: application/octet-stream\n')
        fn = "%s.txt" % (stations[0],)
        if len(stations) > 1:
            fn = "asos.txt"
        ssw('Content-Disposition: attachment; filename=%s\n\n' % (
                         fn,))
    else:
        ssw("Content-type: text/plain \n\n")

    dbstations = stations
    if len(dbstations) == 1:
        dbstations.append('XYZXYZ')

    sts, ets = get_time_bounds(form, tzinfo)

    delim = form.getfirst("format", "onlycomma")
    # How should null values be represented
    missing = NULLS.get(form.getfirst('missing'), "M")
    # How should trace values be represented
    trace = TRACE_OPTS.get(form.getfirst('trace'), "T")

    querycols = build_querycols(form)

    if delim in ["tdf", "onlytdf"]:
        rD = "\t"
    else:
        rD = ","

    gtxt = build_gisextra(form, dbstations, rD)
    gisextra = (form.getfirst("latlon", "no") == "yes")

    rlimiter = ""
    if len(report_type) == 1:
        rlimiter = " and report_type = %s" % (int(report_type[0]),)
    elif len(report_type) > 1:
        rlimiter = (" and report_type in %s"
                    ) % (tuple([int(a) for a in report_type]), )
    sqlcols = ",".join(querycols)
    acursor.execute("""
        SELECT station, valid, """ + sqlcols + """ from alldata
        WHERE valid >= %s and valid < %s and station in %s """+rlimiter+"""
        ORDER by valid ASC
    """, (sts, ets, tuple(dbstations)))

    if delim not in ['onlytdf', 'onlycomma']:
        ssw("#DEBUG: Format Typ    -> %s\n" % (delim,))
        ssw("#DEBUG: Time Period   -> %s %s\n" % (sts, ets))
        ssw("#DEBUG: Time Zone     -> %s\n" % (tzinfo,))
        ssw(("#DEBUG: Data Contact   -> daryl herzmann "
             "akrherz@iastate.edu 515-294-5978\n"))
        ssw("#DEBUG: Entries Found -> %s\n" % (acursor.rowcount,))
    ssw("station"+rD+"valid"+rD)
    if gisextra:
        ssw("lon%slat%s" % (rD, rD))
    # hack to convert tmpf as tmpc to tmpc
    ssw("%s\n" % (rD.join([c.split(" as ")[-1] for c in querycols]), ))

    ff = {
        'wxcodes': fmt_wxcodes,
        'metar': fmt_simple,
        'skyc1': fmt_simple,
        'skyc2': fmt_simple,
        'skyc3': fmt_simple,
        'skyc4': fmt_simple,
        'p01i': fmt_trace,
        'p01i * 25.4 as p01m': fmt_trace,
        'ice_accretion_1hr': fmt_trace,
        'ice_accretion_3hr': fmt_trace,
        'ice_accretion_6hr': fmt_trace,
    }
    # The default is the %.2f formatter
    formatters = [ff.get(col, fmt_f2) for col in querycols]

    gismiss = "%s%s%s%s" % (missing, rD, missing, rD)
    for row in acursor:
        ssw(row[0] + rD)
        ssw((row[1].astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M") + rD)
        if gisextra:
            ssw(gtxt.get(row[0], gismiss))
        ssw(rD.join(
            [func(val, missing, trace)
             for func, val in zip(formatters, row[2:])]) + "\n")


if __name__ == '__main__':
    main()
