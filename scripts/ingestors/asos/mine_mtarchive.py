"""attempt to rip out the METARs stored with the MTarchive files"""
from __future__ import print_function
import datetime
import subprocess
import re
import os
import sys

import requests
import pytz
import pandas as pd
from pyiem.util import get_dbconn

DUP = re.compile("[0-9]{3} SA..[0-9][0-9] [A-Z]{3,4}")
PROD = re.compile("[A-Z0-9]{3,4} [0-3][0-9][0-2][0-9][0-5][0-9]Z ")

XREF = {}


def load_stations():
    pgconn = get_dbconn('mesosite', user='nobody')
    cursor = pgconn.cursor()
    cursor.execute("""
    SELECT id, tzname from stations where network ~* 'ASOS'
    and tzname not in ('UTC+4', 'UTC-3', 'UTC-5')
    """)
    for row in cursor:
        XREF[row[0]] = pytz.timezone(row[1])


def write(ts, stid, obs):

    files = dict()
    for ts, ob in obs.iteritems():
        fn = ts.strftime("%Y%m%d.txt")
        a = files.setdefault(fn, [])
        a.append(ob)
    lsid = stid
    if len(stid) == 4 and stid[0] == 'K':
        lsid = stid[1:]
    mydir = ("/mesonet/ARCHIVE/wunder/cache/%s/%s"
             ) % (lsid, ts.year)
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    for fn, obs in files.iteritems():
        fn2 = "%s/%s" % (mydir, fn)
        # remove old files that had no data at all
        if (os.path.isfile(fn2) and
                open(fn2).read().find("No daily or hourly history ") > -1):
            os.unlink(fn2)
        if os.path.isfile(fn2):
            if open(fn2).read().startswith("FullMetar,"):
                try:
                    df = pd.read_csv(fn2)
                except Exception:
                    print(fn2)
                    return
            else:
                try:
                    df = pd.read_csv(fn2, skiprows=[0, ])
                except Exception:
                    print(fn2)
                    return
            df2 = pd.DataFrame({'FullMetar': obs})
            df = df.append(df2, ignore_index=True)
            series = df['FullMetar'].unique()
            o = open(fn2, 'w')
            o.write("FullMetar,\n")
            for s in series:
                o.write("%s,\n" % (s,))
            o.close()
        else:
            # We are good to overwrite
            o = open(fn2, 'w')
            o.write("FullMetar,\n")
            obs.sort()
            for ob in obs:
                o.write("%s,\n" % (ob.replace(",", " "),))
            o.close()


def compute_ts(stid, ts, token):
    _stid = stid if stid[0] != 'K' else stid[1:]
    ddhhmmz = token.split()[1]
    try:
        ts2 = datetime.datetime(ts.year, ts.month, ts.day, int(ddhhmmz[2:4]),
                                int(ddhhmmz[4:6]))
    except Exception:
        print("Invalid timestamp %s" % (ddhhmmz,))
        return None
    ts2 = ts2.replace(tzinfo=pytz.timezone("UTC"))
    if ts2.strftime("%d") != ddhhmmz[:2]:
        ts2 -= datetime.timedelta(days=1)
    if ts2.strftime("%d") != ddhhmmz[:2]:
        return None
    return ts2.astimezone(XREF.get(_stid, pytz.timezone("UTC")))


def do_stid(archive, ts, stid):
    if len(stid) not in [3, 4]:
        return 0
    o = open('fn', 'w')
    o.write("""
SFFILE = /mesonet/tmp/mtsf.gem
AREA = @%s
DATTIM = ALL
SFPARM = TEXT
OUTPUT   = f/fn2
IDNTYP   = STID
run

exit
""" % (stid,))
    o.close()
    r = subprocess.Popen("timeout 30 sflist < fn", stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    # need to make this sync, so that fn2 is accurate
    r.stdout.read()
    data = open('fn2').read().replace("\n", " ").strip()
    poss = [q.start() for q in PROD.finditer(data)]
    cnt = 0
    for i, pos in enumerate(poss[:-1]):
        token = data[pos:poss[i+1]].strip()
        m = DUP.search(token)
        if m:
            token = token[:m.start()]
        _stid = token.split()[0]
        a = archive.setdefault(_stid, dict())
        ts2 = compute_ts(_stid, ts, token)
        if ts2 is not None:
            a[ts2] = token
        cnt += 1
    return cnt
    # 5. save these in the proper /mesonet/ARCHIVE/cache Folder


def workflow(ts):
    # 1. Get mtarchive file
    uri = ts.strftime(("http://mtarchive.geol.iastate.edu/%Y/%m/%d/gempak/"
                       "surface/sao/%Y%m%d_sao.gem"))
    req = requests.get(uri, timeout=30)
    if req.status_code != 200:
        print('Whoa! %s %s' % (req.status, uri))
        return
    fh = open("/mesonet/tmp/mtsf.gem", 'wb')
    fh.write(req.content)
    fh.close()
    # 2. run sflist to extract all stations
    fh = open('fn', 'w')
    fh.write("""
SFFILE = /mesonet/tmp/mtsf.gem
AREA = ALL
DATTIM = ALL
SFPARM = STID
OUTPUT   = T
IDNTYP   = STID
list
run

exit
""")
    fh.close()
    proc = subprocess.Popen("sflist < fn", stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    data = proc.stdout.read()
    stations = {}
    for line in data.split("\n"):
        tokens = line.strip().split()
        if len(tokens) != 3:
            continue
        if tokens[0] not in XREF:
            continue
        stations[tokens[0]] = True
    # 3. loop over each station, sigh
    archive = dict()
    res = [do_stid(archive, ts, stid) for stid in stations]
    print("Found %s stations, %s obs for %s" % (len(stations), sum(res),
                                                ts.strftime("%Y%m%d")))
    for stid, obs in archive.iteritems():
        write(ts, stid, obs)


def main(argv):
    """Go Main Go"""
    load_stations()
    workflow(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))


if __name__ == '__main__':
    main(sys.argv)
