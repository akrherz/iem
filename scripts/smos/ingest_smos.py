"""Ingest SMOS data, please!"""
import glob
import os
import re
import datetime
from io import StringIO
import warnings

import pytz
from pyiem.util import get_dbconn, ncopen, logger

LOG = logger()
TSTAMP = re.compile("([0-9]{8}T[0-9]{6})")
warnings.simplefilter("ignore", category=DeprecationWarning)


def consume(scursor, fn, ts, grid_ids):
    """Actually process the filename at given timestamp
    """
    table = "data_%s" % (ts.strftime("%Y_%m"),)
    LOG.debug("Processing %s for table %s", fn, table)
    nc = ncopen(fn)
    gpids = nc.variables["Grid_Point_ID"][:]
    sms = nc.variables["Soil_Moisture"][:].tolist()
    optdepths = nc.variables["Optical_Thickness_Nad"][:].tolist()
    chi2pds = nc.variables["Chi_2_P"][:].tolist()
    bad = 0
    good = 0
    data = StringIO()
    for gpid, sm, od, chi2pd in zip(gpids, sms, optdepths, chi2pds):
        if int(gpid) not in grid_ids:
            continue
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
    return ts.replace(tzinfo=pytz.UTC)


def load_grid_ids(scursor, grid_ids):
    """Figure out which grid IDs we know."""
    scursor.execute("SELECT idx from grid")
    for row in scursor:
        grid_ids.append(row[0])


def lookforfiles():
    """Look for any new data to ingest"""
    pgconn = get_dbconn("smos")
    scursor = pgconn.cursor()
    os.chdir("/mesonet/data/smos")
    files = glob.glob("*.nc")
    grid_ids = []
    for fn in files:
        ts = fn2datetime(fn)
        if ts is None:
            LOG.info("ingest_smos: fn2datetime fail: %s", fn)
            continue
        scursor.execute("SELECT * from obtimes where valid = %s", (ts,))
        row = scursor.fetchone()
        if row is None:
            if not grid_ids:
                load_grid_ids(scursor, grid_ids)
            consume(scursor, fn, ts, grid_ids)
            scursor.execute("INSERT into obtimes(valid) values (%s)", (ts,))
            pgconn.commit()


if __name__ == "__main__":
    lookforfiles()
