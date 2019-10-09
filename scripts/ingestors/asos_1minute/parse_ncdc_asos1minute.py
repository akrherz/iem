"""
 Attempt to process the 1 minute archives available from NCDC

 NCDC provides monthly tar files for nearly up to the current day here:

 https://www1.ncdc.noaa.gov/pub/download/hidden/onemin/
"""
from __future__ import print_function
import re
import os
import subprocess
import sys
import datetime

import pytz
import requests
from pyiem.util import get_dbconn, logger

LOG = logger()
BASEDIR = "/mesonet/ARCHIVE/raw/asos/"

P1_RE = re.compile(r"""
(?P<wban>[0-9]{5})
(?P<faaid>[0-9A-Z]{4})\s
(?P<id3>[0-9A-Z]{3})
(?P<tstamp>[0-9]{16})\s+
((?P<vis1_coef>\-?\d+\.\d*)|(?P<vis1_coef_miss>M))\s*\s*
(?P<vis1_nd>[0-9A-Za-z\?\$/ ])\s+
((?P<vis2_coef>\d+\.\d*)|(?P<vis2_coef_miss>[M ]))\s+
(?P<vis2_nd>[A-Za-z\?\$ ])\s+
...............\s+
((?P<drct>\d+)|(?P<drct_miss>M))\s+
((?P<sknt>\d+)|(?P<sknt_miss>M))\s+
((?P<gust_drct>\d+)\+?|(?P<gust_drct_miss>M))\s+
((?P<gust_sknt>\d+)R?L?F*\d*\+?|(?P<gust_sknt_miss>M))\s+
(....)\s
(...)
""", re.VERBOSE)

p1_examples = open('p1_examples.txt').readlines()

P2_RE = re.compile(r"""
(?P<wban>[0-9]{5})
(?P<faaid>[0-9A-Z]{4})\s
(?P<id3>[0-9A-Z]{3})
(?P<tstamp>[0-9]{16})\s+
\s?(?P<ptype>[a-zA-Z0-9\?\-\+\.]{1,2})\s?\s?\s?
((?P<unk>\d+)V?|\s+(?P<unk_miss>[M ]))\s+\s?
\s*((?P<precip>\d+\.\d*)|(?P<precip_miss>[M ]))\s*
............\s+
((?P<unk2>\d*)|(?P<unk2_miss>M))\s+
((?P<pres1>\d+\.\d*)|(?P<pres1_miss>[M ]))\s*
((?P<pres2>\d+\.\d*)|(?P<pres2_miss>[M ]))\s*
((?P<pres3>\d+\.\d*)|(?P<pres3_miss>[M ]))\s*
\s*((?P<tmpf>\-?\d+)|(?P<tmpf_miss>[M ]))\s*
\s*((?P<dwpf>\-?\d+)|(?P<dwpf_miss>[M ]))\s+
""", re.VERBOSE)


p2_examples = open('p2_examples.txt').readlines()


def tstamp2dt(s):
    """ Convert a string to a datetime """
    ts = datetime.datetime(int(s[:4]), int(s[4:6]), int(s[6:8]))
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    local_hr = int(s[8:10])
    utc_hr = int(s[12:14])
    if utc_hr < local_hr:  # Next day assumption valid in United States
        ts += datetime.timedelta(hours=24)
    return ts.replace(hour=utc_hr, minute=int(s[14:16]))


def p2_parser(ln):
    """
    Handle the parsing of a line found in the 6506 report, return QC dict
    """
    m = P2_RE.match(ln.replace("]", "").replace("[", ""))
    if m is None:
        print("P2_FAIL:|%s|" % (ln,))
        return None
    res = m.groupdict()
    res['ts'] = tstamp2dt(res['tstamp'])
    return res


def p1_parser(ln):
    """
    Handle the parsing of a line found in the 6505 report, return QC dict
    """
    m = P1_RE.match(ln.replace("]", "").replace("[", ""))
    if m is None:
        print("P1_FAIL:|%s|" % (ln,))
        return None
    res = m.groupdict()
    res['ts'] = tstamp2dt(res['tstamp'])
    return res


def download(station, monthts):
    """
    Download a month file from NCDC
    """
    baseuri = "https://www1.ncdc.noaa.gov/pub/data/asos-onemin/"
    datadir = "%s/data/%s" % (BASEDIR, station)
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
    for page in [5, 6]:
        uri = baseuri + "640%s-%s/640%s0K%s%s.dat" % (page, monthts.year, page,
                                                      station,
                                                      monthts.strftime("%Y%m"))
        req = requests.get(uri)
        if req.status_code != 200:
            LOG.info("dl %s failed with code %s", uri, req.status_code)
            continue
        with open(
            "%s/640%s0K%s%s.dat" % (
                datadir, page, station, monthts.strftime("%Y%m")), 'wb') as fp:
            fp.write(req.content)


def runner(station, monthts):
    """
    Parse a month's worth of data please
    """

    # Our final amount of data
    data = {}
    if os.path.isfile("64050K%s%s%02i" % (station, monthts.year,
                                          monthts.month)):
        fn5 = '64050K%s%s%02i' % (station, monthts.year, monthts.month)
        fn6 = '64060K%s%s%02i' % (station, monthts.year, monthts.month)
    else:
        fn5 = ('%sdata/%s/64050K%s%s%02i.dat'
               ) % (BASEDIR, station,
                    station, monthts.year, monthts.month)
        fn6 = ('%sdata/%s/64060K%s%s%02i.dat'
               ) % (BASEDIR, station,
                    station, monthts.year, monthts.month)
        if not os.path.isfile(fn5):
            try:
                download(station, monthts)
            except Exception as exp:
                print('download() error %s' % (exp,))
            if not os.path.isfile(fn5) or not os.path.isfile(fn6):
                print(("NCDC did not have %s station for %s"
                       ) % (station, monthts.strftime("%b %Y")))
                return
    # We have two files to worry about
    print("Processing 64050: %s" % (fn5,))
    for ln in open(fn5):
        d = p1_parser(ln)
        if d is None:
            continue
        data[d['ts']] = d

    print("Processing 64060: %s" % (fn6,))
    for ln in open(fn6):
        d = p2_parser(ln)
        if d is None:
            continue
        if d['ts'] not in data:
            data[d['ts']] = {}
        for k in d.keys():
            data[d['ts']][k] = d[k]

    if not data:
        print('No data found for station: %s' % (station,))
        return

    mints = None
    maxts = None
    for ts in data:
        if mints is None or maxts is None:
            mints = ts
            maxts = ts
        if mints > ts:
            mints = ts
        if maxts < ts:
            maxts = ts

    tmpfn = "/tmp/%s%s-dbinsert.sql" % (station, monthts.strftime("%Y%m"))
    out = open(tmpfn, 'w')
    out.write("""DELETE from alldata_1minute WHERE station = '%s' and
               valid >= '%s' and valid <= '%s';\n""" % (station, mints, maxts))
    out.write("COPY t%s_1minute FROM stdin WITH NULL as 'Null';\n" % (
         monthts.year,))

    # Loop over the data we got please
    keys = list(data.keys())
    keys.sort()
    flipped = False
    for ts in keys:
        if ts.year != monthts.year and not flipped:
            print("  Flipped years from %s to %s" % (monthts.year, ts.year))
            out.write("\.\n")
            out.write(("COPY t%s_1minute FROM stdin WITH NULL as 'Null';\n"
                       ) % (ts.year,))
            flipped = True
        ln = ""
        data[ts]['station'] = station
        for col in ['station', 'ts', 'vis1_coeff', 'vis1_nd',
                    'vis2_coeff', 'vis2_nd', 'drct', 'sknt', 'gust_drct',
                    'gust_sknt', 'ptype', 'precip', 'pres1', 'pres2', 'pres3',
                    'tmpf', 'dwpf']:
            ln += "%s\t" % (data[ts].get(col) or 'Null',)
        out.write(ln[:-1]+"\n")
    out.write("\.\n")
    out.close()

    proc = subprocess.Popen(
        "psql -f %s -h iemdb-asos.local asos" % (tmpfn,), shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.read().decode('utf-8')
    stderr = proc.stderr.read().decode('utf-8')

    print(("%s %s processed %s entries [%s to %s UTC]\n"
           "STDOUT: %s\nSTDERR: %s"
           ) % (datetime.datetime.now().strftime("%H:%M %p"),
                station, len(data.keys()), mints.strftime("%y%m%d %H:%M"),
                maxts.strftime("%y%m%d %H:%M"), stdout.replace("\n", " "),
                stderr.replace("\n", " ")))

    if stderr == '':
        os.unlink(tmpfn)


def update_iemprops():
    """db update"""
    pgconn = get_dbconn('mesosite')
    cursor = pgconn.cursor()
    m1 = datetime.date.today().replace(day=1)
    cursor.execute("""
        UPDATE properties SET propvalue = %s
        WHERE propname = 'asos.1min.end'
    """, (m1.strftime("%Y-%m-%d"),))
    cursor.close()
    pgconn.commit()


def main(argv):
    """Go Main Go"""
    if len(argv) == 3:
        for station in ["DVN", "LWD", "FSD", "MLI", 'OMA', 'MCW', 'BRL', 'AMW',
                        'MIW', 'SPW', 'OTM', 'CID', 'EST', 'IOW', 'SUX', 'DBQ',
                        'ALO', 'DSM']:
            runner(station,
                   datetime.datetime(int(argv[1]), int(argv[2]), 1))
    elif len(argv) == 4:
        if int(argv[3]) != 0:
            months = [int(argv[3]), ]
        else:
            months = range(1, 13)
        for month in months:
            runner(sys.argv[1], datetime.datetime(int(argv[2]), month, 1))
    else:
        # default to last month
        ts = datetime.date.today() - datetime.timedelta(days=19)
        for station in ["DVN", "LWD", "FSD", "MLI", 'OMA', 'MCW', 'BRL', 'AMW',
                        'MIW', 'SPW', 'OTM', 'CID', 'EST', 'IOW', 'SUX', 'DBQ',
                        'ALO', 'DSM']:
            runner(station,
                   datetime.datetime(ts.year, ts.month, 1))
        update_iemprops()


if __name__ == '__main__':
    main(sys.argv)


def test_parser():
    """test things"""
    for ex in p1_examples:
        p1_parser(ex)

    for ex in p2_examples:
        p2_parser(ex)
