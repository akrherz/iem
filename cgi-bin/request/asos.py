#!/usr/bin/env python
"""
Download interface for ASOS/AWOS data from the asos database
"""
import time
import cgi
import re
import os
import sys
import datetime
import pytz
import psycopg2.extras
from pyiem.datatypes import temperature, speed
from pyiem import meteorology


def check_load():
    """Prevent automation from overwhelming the server"""
    for i in range(5):
        pgconn = psycopg2.connect(database='mesosite', host='iemdb',
                                  user='nobody')
        mcursor = pgconn.cursor()
        mcursor.execute("""
        select pid from pg_stat_activity where query ~* 'FETCH'
        and datname = 'asos'""")
        if mcursor.rowcount < 10:
            return
        pgconn.close()
        if i == 4:
            sys.stderr.write(("[client: %s] "
                              "/cgi-bin/request/asos.py over capacity: %s\n"
                              ) % (os.environ.get('REMOTE_ADDR'),
                                   mcursor.rowcount))
        else:
            time.sleep(3)
    sys.stdout.write("Content-type: text/plain \n")
    sys.stdout.write('Status: 503 Service Unavailable\n\n')
    sys.stdout.write("ERROR: server over capacity, please try later")
    sys.exit(0)


def get_stations(form):
    """ Figure out the requested station """
    if "station" not in form:
        sys.stdout.write("Content-type: text/plain \n\n")
        sys.stdout.write("ERROR: station must be specified!")
        sys.exit(0)
    stations = form.getlist("station")
    if len(stations) == 0:
        sys.stdout.write("Content-type: text/plain \n\n")
        sys.stdout.write("ERROR: station must be specified!")
        sys.exit(0)
    return stations


def get_time_bounds(form, tzinfo):
    """ Figure out the exact time bounds desired """
    y1 = int(form.getfirst('year1'))
    y2 = int(form.getfirst('year2'))
    m1 = int(form.getfirst('month1'))
    m2 = int(form.getfirst('month2'))
    d1 = int(form.getfirst('day1'))
    d2 = int(form.getfirst('day2'))
    # Construct dt instances in the right timezone, this logic sucks, but is
    # valid, have to go to UTC first then back to the local timezone
    sts = datetime.datetime.utcnow()
    sts = sts.replace(tzinfo=pytz.timezone("UTC"))
    sts = sts.astimezone(tzinfo)
    ets = sts
    try:
        sts = sts.replace(year=y1, month=m1, day=d1, hour=0, minute=0,
                          second=0, microsecond=0)
        ets = sts.replace(year=y2, month=m2, day=d2, hour=0, minute=0,
                          second=0, microsecond=0)
    except:
        sys.stdout.write("ERROR: Malformed Date!")
        sys.exit()

    if sts == ets:
        ets += datetime.timedelta(days=1)

    return sts, ets


def main():
    """ Go main Go """
    check_load()
    form = cgi.FieldStorage()
    try:
        tzinfo = pytz.timezone(form.getfirst("tz", "Etc/UTC"))
    except pytz.exceptions.UnknownTimeZoneError as exp:
        sys.stdout.write("Content-type: text/plain\n\n")
        sys.stdout.write("Invalid Timezone (tz) provided")
        sys.stderr.write("asos.py invalid tz: %s\n" % (exp, ))
        sys.exit()
    pgconn = psycopg2.connect(database='asos', host='iemdb', user='nobody')
    acursor = pgconn.cursor('mystream',
                            cursor_factory=psycopg2.extras.DictCursor)

    # Save direct to disk or view in browser
    direct = True if form.getfirst('direct', 'no') == 'yes' else False
    report_type = form.getlist('report_type')
    stations = get_stations(form)
    if direct:
        sys.stdout.write('Content-type: application/octet-stream\n')
        fn = "%s.txt" % (stations[0],)
        if len(stations) > 1:
            fn = "asos.txt"
        sys.stdout.write('Content-Disposition: attachment; filename=%s\n\n' % (
                         fn,))
    else:
        sys.stdout.write("Content-type: text/plain \n\n")

    dbstations = stations
    if len(dbstations) == 1:
        dbstations.append('XYZXYZ')

    dataVars = form.getlist("data")
    sts, ets = get_time_bounds(form, tzinfo)

    delim = form.getfirst("format", "onlycomma")

    if "all" in dataVars:
        queryCols = ("tmpf, dwpf, relh, drct, sknt, p01i, alti, mslp, "
                     "vsby, gust, skyc1, skyc2, skyc3, skyc4, skyl1, "
                     "skyl2, skyl3, skyl4, presentwx, metar")
        outCols = ['tmpf', 'dwpf', 'relh', 'drct', 'sknt', 'p01i', 'alti',
                   'mslp', 'vsby', 'gust', 'skyc1', 'skyc2', 'skyc3',
                   'skyc4', 'skyl1', 'skyl2', 'skyl3', 'skyl4',
                   'presentwx', 'metar']
    else:
        for _colname in ['station', 'valid']:
            if _colname in dataVars:
                dataVars.remove(_colname)
        dataVars = tuple(dataVars)
        outCols = dataVars
        dataVars = str(dataVars)[1:-2]
        queryCols = re.sub("'", " ", dataVars)

    if delim in ["tdf", "onlytdf"]:
        rD = "\t"
        queryCols = re.sub(",", "\t", queryCols)
    else:
        rD = ","

    gtxt = {}
    gisextra = False
    if form.getfirst("latlon", "no") == "yes":
        gisextra = True
        MESOSITE = psycopg2.connect(database='mesosite', host='iemdb',
                                    user='nobody')
        mcursor = MESOSITE.cursor()
        mcursor.execute("""SELECT id, ST_x(geom) as lon, ST_y(geom) as lat
             from stations WHERE id in %s
             and (network ~* 'AWOS' or network ~* 'ASOS')
        """, (tuple(dbstations),))
        for row in mcursor:
            gtxt[row[0]] = "%.4f%s%.4f%s" % (row[1], rD, row[2], rD)

    rlimiter = ""
    if len(report_type) == 1:
        rlimiter = " and report_type = %s" % (int(report_type[0]),)
    elif len(report_type) > 1:
        rlimiter = (" and report_type in %s"
                    ) % (tuple([int(a) for a in report_type]), )
    acursor.execute("""SELECT * from alldata
      WHERE valid >= %s and valid < %s and station in %s """+rlimiter+"""
      ORDER by valid ASC""", (sts, ets, tuple(dbstations)))

    if delim not in ['onlytdf', 'onlycomma']:
        sys.stdout.write("#DEBUG: Format Typ    -> %s\n" % (delim,))
        sys.stdout.write("#DEBUG: Time Period   -> %s %s\n" % (sts, ets))
        sys.stdout.write("#DEBUG: Time Zone     -> %s\n" % (tzinfo,))
        sys.stdout.write(("#DEBUG: Data Contact   -> daryl herzmann "
                          "akrherz@iastate.edu 515-294-5978\n"))
        sys.stdout.write("#DEBUG: Entries Found -> %s\n" % (acursor.rowcount,))
    sys.stdout.write("station"+rD+"valid"+rD)
    if gisextra:
        sys.stdout.write("lon"+rD+"lat"+rD)
    sys.stdout.write(queryCols+"\n")

    for row in acursor:
        sys.stdout.write(row["station"] + rD)
        sys.stdout.write(
            (row["valid"].astimezone(tzinfo)).strftime("%Y-%m-%d %H:%M") + rD)
        if gisextra:
            sys.stdout.write(gtxt.get(row['station'], "M%sM%s" % (rD, rD)))
        r = []
        for data1 in outCols:
            if data1 == 'relh':
                if row['tmpf'] is not None and row['dwpf'] is not None:
                    tmpf = temperature(row['tmpf'], 'F')
                    dwpf = temperature(row['dwpf'], 'F')
                    val = meteorology.relh(tmpf, dwpf)
                    r.append("%.2f" % (val.value("%"),))
                else:
                    r.append("M")
            elif data1 == 'sped':
                if row['sknt'] >= 0:
                    r.append("%.1f" % (speed(row['sknt'],
                                             'KT').value('MPH'), ))
                else:
                    r.append("M")
            elif data1 == 'gust_mph':
                if row['gust'] >= 0:
                    r.append("%.1f" % (speed(row['gust'],
                                             'KT').value('MPH'), ))
                else:
                    r.append("M")
            elif data1 == 'p01m':
                if row['p01i'] >= 0:
                    r.append("%.2f" % (row['p01i'] * 25.4, ))
                else:
                    r.append("M")
            elif data1 == 'tmpc':
                if row['tmpf'] is not None:
                    val = temperature(row['tmpf'], 'F').value('C')
                    r.append("%.2f" % (val, ))
                else:
                    r.append("M")
            elif data1 == 'dwpc':
                if row['dwpf'] is not None:
                    val = temperature(row['dwpf'], 'F').value('C')
                    r.append("%.2f" % (val, ))
                else:
                    r.append("M")
            elif data1 == 'presentwx':
                if row['presentwx'] is not None:
                    r.append("%s" % (row['presentwx'].replace(",", " "), ))
                else:
                    r.append("M")
            elif data1 in ["metar", "skyc1", "skyc2", "skyc3", "skyc4"]:
                if row[data1] is None:
                    r.append("M")
                else:
                    r.append("%s" % (row[data1].replace(",", " "), ))
            elif (row.get(data1) is None or row[data1] <= -99.0 or
                  row[data1] == "M"):
                r.append("M")
            else:
                r.append("%2.2f" % (row[data1], ))
        sys.stdout.write("%s\n" % (rD.join(r),))


if __name__ == '__main__':
    main()
