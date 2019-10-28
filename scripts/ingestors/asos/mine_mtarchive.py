"""attempt to rip out the METARs stored with the MTarchive files"""
from __future__ import print_function
import datetime
import subprocess
import re
import os
import sys

import requests
from pyiem.util import get_dbconn, utc

DUP = re.compile("[0-9]{3} SA..[0-9][0-9] [A-Z]{3,4}")
PROD = re.compile("[A-Z0-9]{3,4} [0-3][0-9][0-2][0-9][0-5][0-9]Z ")

XREF = {}
NETWORKS = []


def load_stations():
    """Get station timezone info?"""
    pgconn = get_dbconn("mesosite", user="nobody")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT id, network from stations where network ~* 'ASOS'
    """
    )
    for row in cursor:
        XREF[row[0]] = row[1]


def do_stid(stid):
    """Go."""
    pgconn = get_dbconn("asos")
    cursor = pgconn.cursor()
    if len(stid) not in [3, 4]:
        return 0
    with open("fn", "w") as fh:
        # NB: not all GEMPAK surface files stored the raw METAR, so using
        # TEXT here may not always work.
        fh.write(
            """
SFFILE = /mesonet/tmp/mtsf.gem
AREA = @%s
DATTIM = ALL
SFPARM = TMPF
OUTPUT   = f/fn2
IDNTYP   = STID
run

exit
"""
            % (stid,)
        )
    r = subprocess.Popen(
        "timeout 30 /tmp/sflist < fn",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    # need to make this sync, so that fn2 is accurate
    r.stdout.read()
    if not os.path.isfile("fn2"):
        return 0
    for line in open("fn2"):
        tokens = line.strip().split()
        if len(tokens) != 3:
            continue
        try:
            ts = datetime.datetime.strptime(tokens[1], "%y%m%d/%H%M")
        except ValueError:
            continue
        tmpf = float(tokens[2])
        # missing
        if tmpf < -9000:
            continue
        valid = utc(ts.year, ts.month, ts.day, ts.hour, ts.minute)
        cursor.execute(
            """
            SELECT tmpf from alldata where station = %s and valid = %s
            and tmpf is not null
        """,
            (stid, valid),
        )
        if cursor.rowcount == 0:
            print("%s %s no results" % (stid, valid))
            continue
        row = cursor.fetchone()
        delta = abs(row[0] - tmpf)
        if delta > 1:
            network = XREF.get(stid)
            if network not in NETWORKS:
                NETWORKS.append(network)
            print(
                "%s[%s] %s old: %s new: %s"
                % (stid, network, valid, row[0], tmpf)
            )
    return 0
    # 5. save these in the proper /mesonet/ARCHIVE/cache Folder


def workflow(ts):
    """We do work."""
    # 1. Get mtarchive file
    uri = ts.strftime(
        (
            "http://mtarchive.geol.iastate.edu/%Y/%m/%d/gempak/"
            "surface/sao/%Y%m%d_sao.gem"
        )
    )
    req = requests.get(uri, timeout=30)
    if req.status_code != 200:
        print("Whoa! %s %s" % (req.status, uri))
        return
    with open("/mesonet/tmp/mtsf.gem", "wb") as fh:
        fh.write(req.content)
    # 2. run sflist to extract all stations
    with open("fn", "w") as fh:
        fh.write(
            """
SFFILE = /mesonet/tmp/mtsf.gem
AREA = ALL
DATTIM = ALL
SFPARM = STID
OUTPUT   = T
IDNTYP   = STID
list
run

exit
"""
        )
    proc = subprocess.Popen(
        "/tmp/sflist < fn",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    data = proc.stdout.read().decode("ascii", "ignore")
    stations = {}
    for line in data.split("\n"):
        tokens = line.strip().split()
        if len(tokens) != 3:
            continue
        if tokens[0] not in XREF:
            continue
        stations[tokens[0]] = True
    # 3. loop over each station, sigh
    res = [do_stid(stid) for stid in stations]
    print(
        "Found %s stations, %s obs for %s"
        % (len(stations), sum(res), ts.strftime("%Y%m%d"))
    )
    print(NETWORKS)


def main(argv):
    """Go Main Go"""
    load_stations()
    workflow(datetime.date(int(argv[1]), int(argv[2]), int(argv[3])))


if __name__ == "__main__":
    main(sys.argv)
