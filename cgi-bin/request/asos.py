#!/usr/bin/env python
"""
Download interface for ASOS/AWOS data from the asos database
"""

import cgi
import re
import sys
import datetime
import pytz
import psycopg2.extras
from pyiem.datatypes import temperature
from pyiem import meteorology

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
acursor = ASOS.cursor(cursor_factory=psycopg2.extras.DictCursor)
MESOSITE = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)


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
    form = cgi.FieldStorage()
    try:
        tzinfo = pytz.timezone(form.getfirst("tz", "Etc/UTC"))
    except:
        sys.stdout.write("Invalid Timezone (tz) provided")
        sys.exit()

    # Save direct to disk or view in browser
    direct = True if form.getfirst('direct', 'no') == 'yes' else False
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

    delim = form.getfirst("format")

    if "all" in dataVars:
        queryCols = ("tmpf, dwpf, relh, drct, sknt, p01i, alti, mslp, "
                     "vsby, gust, skyc1, skyc2, skyc3, skyc4, skyl1, "
                     "skyl2, skyl3, skyl4, presentwx, metar")
        outCols = ['tmpf', 'dwpf', 'relh', 'drct', 'sknt', 'p01i', 'alti',
                   'mslp', 'vsby', 'gust', 'skyc1', 'skyc2', 'skyc3',
                   'skyc4', 'skyl1', 'skyl2', 'skyl3', 'skyl4',
                   'presentwx', 'metar']
    else:
        dataVars = tuple(dataVars)
        outCols = dataVars
        dataVars = str(dataVars)[1:-2]
        queryCols = re.sub("'", " ", dataVars)

    if delim == "tdf":
        rD = "\t"
        queryCols = re.sub(",", "\t", queryCols)
    else:
        rD = ","

    gtxt = {}
    gisextra = False
    if form.getfirst("latlon", "no") == "yes":
        gisextra = True
        mcursor.execute("""SELECT id, ST_x(geom) as lon, ST_y(geom) as lat
             from stations WHERE id in %s
             and (network ~* 'AWOS' or network ~* 'ASOS')
        """, (tuple(dbstations),))
        for row in mcursor:
            gtxt[row[0]] = "%.4f%s%.4f%s" % (row['lon'], rD, row['lat'], rD)

    acursor.execute("""SELECT * from alldata
      WHERE valid >= %s and valid < %s and station in %s
      ORDER by valid ASC""", (sts, ets, tuple(dbstations)))

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
                    r.append("%.1f" % (row['sknt'] * 1.14, ))
                else:
                    r.append("M")
            elif data1 == 'gust_mph':
                if row['gust'] >= 0:
                    r.append("%.1f" % (row['gust'] * 1.14, ))
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
                    r.append("%s" % (row[data1], ))
            elif (row[data1] is None or row[data1] <= -99.0 or
                  row[data1] == "M"):
                r.append("M")
            else:
                r.append("%2.2f" % (row[data1], ))
        sys.stdout.write("%s\n" % (rD.join(r),))

if __name__ == '__main__':
    main()
