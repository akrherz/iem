"""Ingest SMOS data, please!"""
from __future__ import print_function
import glob
import os
import re
import datetime
from io import StringIO

import pytz
from pyiem.util import get_dbconn, ncopen

TSTAMP = re.compile("([0-9]{8}T[0-9]{6})")


def consume(scursor, fn, ts):
    """Actually process the filename at given timestamp
    """
    table = "data_%s" % (ts.strftime("%Y_%m"),)
    nc = ncopen(fn)
    gpids = nc.variables["Grid_Point_ID"][:]
    sms = nc.variables["Soil_Moisture"][:].tolist()
    optdepths = nc.variables["Optical_Thickness_Nad"][:].tolist()
    chi2pds = nc.variables["Chi_2_P"][:].tolist()
    bad = 0
    good = 0
    data = StringIO()
    for gpid, sm, od, chi2pd in zip(gpids, sms, optdepths, chi2pds):
        # changed 1 Feb 2018 as per guidance from Victoria
        if chi2pd is not None and chi2pd < 0.05:
            bad += 1
            od = None
            sm = None
        if sm is None or sm <= 0 or sm >= 0.7:
            sm = None
        if od is None or od <= 0 or od > 1:
            od = None
        data.write(
            ("%s\t%s\t%s\t%s\n")
            % (
                int(gpid),
                ts.strftime("%Y-%m-%d %H:%M:%S+00"),
                sm or "null",
                od or "null",
            )
        )
        good += 1

    data.seek(0)
    scursor.copy_from(
        data,
        table,
        columns=("grid_idx", "valid", "soil_moisture", "optical_depth"),
        null="null",
    )


def fn2datetime(fn):
    """Convert a filename into a datetime instance

    Example: SM_OPER_MIR_SMUDP2_20161014T002122_20161014T011435_620_001_1.nc
    """
    tokens = TSTAMP.findall(fn)
    if not tokens:
        return None
    ts = datetime.datetime.strptime(tokens[0], "%Y%m%dT%H%M%S")
    return ts.replace(tzinfo=pytz.utc)


def lookforfiles():
    """Look for any new data to ingest"""
    pgconn = get_dbconn("smos")
    scursor = pgconn.cursor()
    os.chdir("/mesonet/data/smos")
    files = glob.glob("*.nc")
    for fn in files:
        ts = fn2datetime(fn)
        if ts is None:
            print("ingest_smos: fn2datetime fail: %s" % (fn,))
            continue
        scursor.execute(
            """
            SELECT * from obtimes where valid = %s
        """,
            (ts,),
        )
        row = scursor.fetchone()
        if row is None:
            # print "INGEST FILE!", file
            consume(scursor, fn, ts)
            scursor.execute(
                """
            INSERT into obtimes(valid) values (%s)
            """,
                (ts,),
            )
            pgconn.commit()


if __name__ == "__main__":
    lookforfiles()
