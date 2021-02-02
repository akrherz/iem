"""
 Attempt to process the 1 minute archives available from NCDC

 NCDC provides monthly tar files for nearly up to the current day here:

 https://www1.ncdc.noaa.gov/pub/download/hidden/onemin/
"""
import re
import codecs
import os
from io import StringIO
import sys
import tarfile
import datetime

import pytz
import pandas as pd
from pandas.io.sql import read_sql
from pyiem.util import get_dbconn, logger, utc, exponential_backoff
import requests
from tqdm import tqdm

LOG = logger()
BASEDIR = "/mesonet/ARCHIVE/raw/asos/data"
TMPDIR = "/mesonet/tmp/asos1min"
if not os.path.isdir(TMPDIR):
    os.makedirs(TMPDIR)

REAL_RE = re.compile(r"^\-?\d+\.\d+$")
INT_RE = re.compile(r"^\-?\d+$")
RUNWAY_RE = re.compile(r" \d+\s\d+\+?\s*$")
DT1980 = utc(1980, 1, 1)


def qc(mydict, col):
    """Primative QC."""
    if col not in mydict:
        return "null"
    val = mydict[col]
    if val is None:
        return "null"
    if col in ["tmpf", "dwpf"]:
        if val < -90 or val > 150:
            return "null"
    if col in ["drct", "gust_drct"]:
        if val < 0 or val > 360:
            return "null"
    if col in ["sknt", "gust_sknt"]:
        if val < 0 or val > 360:
            return "null"
    return val


def tstamp2dt(s):
    """ Convert a string to a datetime """
    if s[0] not in ["1", "2"]:
        LOG.debug("bad timestamp |%s|", s)
        return None
    try:
        ts = datetime.datetime(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except Exception:
        LOG.debug("bad timestamp |%s|", s)
        return None
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
    if len(ln) < 30:
        return None
    res = {
        "wban": ln[:5],
        "faaid": ln[5:9],
        "id3": ln[10:13],
        "tstamp": ln[13:29],
    }
    ln = ln.replace("[", " ").replace("]", " ").replace("\\", " ")
    res["valid"] = tstamp2dt(res["tstamp"])
    if res["valid"] is None:
        return None
    s = ln[31:34].strip()
    res["ptype"] = None if s == "" else s[:2]
    s = ln[44:48].strip()
    res["precip"] = None if not REAL_RE.match(s) else float(s)
    s = ln[69:77].strip()
    res["pres1"] = None if not REAL_RE.match(s) else float(s)
    s = ln[77:85].strip()
    res["pres2"] = None if not REAL_RE.match(s) else float(s)
    s = ln[85:93].strip()
    res["pres3"] = None if not REAL_RE.match(s) else float(s)
    s = ln[94:97].strip()
    res["tmpf"] = None if not INT_RE.match(s) else int(s)
    s = ln[99:102].strip()
    res["dwpf"] = None if not INT_RE.match(s) else int(s)

    return res


def p1_parser(line):
    """
    Handle the parsing of a line found in the 6505 report, return QC dict
    """
    if len(line) < 30:
        return None
    res = {
        "wban": line[:5],
        "faaid": line[5:9],
        "id3": line[10:13],
        "tstamp": line[13:29],
    }
    res["valid"] = tstamp2dt(res["tstamp"])
    if res["valid"] is None:
        return None
    # Ignore [], but leave spaces in their place
    ln = line[30:].replace("[", " ").replace("]", " ").strip()
    # The runway pattern at the end causes pain, remove 90% of the trouble
    ln = re.sub(RUNWAY_RE, " _", ln)
    # Split the rest into tokens
    tokens = ln.split()
    sz = len(tokens)
    # Look for viz pairs, these will be some decimal value followed by 1 char
    vispos = 1
    ints = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.find(".") > -1 and (i + 1) < sz:
            # Corrupt data at this point, abandon ship
            if vispos == 4:
                break
            res[f"vis{vispos}_coef"] = float(token)
            i += 1
            if len(tokens[i]) == 1 and tokens[i].isalpha():
                res[f"vis{vispos}_nd"] = tokens[i]
                i += 1
            vispos += 1
            continue
        # Once we find an int, we are done with viz work and the pain starts
        if token.isalnum() or token == "M":
            # Get the remainder
            ints = tokens[i:]
            # Can we find 4 ints in a row within that list?
            if all([INT_RE.match(t) is not None for t in ints[:4]]):
                ints = ints[:4]
            elif all([INT_RE.match(t) is not None for t in ints[1:5]]):
                ints = ints[1:5]
            else:
                ints = []
            break
        i += 1
    if len(ints) >= 4:
        for i, col in enumerate(["drct", "sknt", "gust_drct", "gust_sknt"]):
            res[col] = None if not INT_RE.match(ints[i]) else int(ints[i])
    # Some gentle QC
    for col in ["sknt", "gust_sknt"]:
        if res.get(col) is not None and res[col] > 125:
            LOG.info("ln: |%s| yielded %s(%s) > 125", line[:-1], col, res[col])
            res[col] = None
    return res


def dl_archive(df, dt):
    """Do archived downloading."""
    baseuri = "https://www1.ncdc.noaa.gov/pub/data/asos-onemin"
    for station in df.index.values:
        datadir = "%s/%s" % (BASEDIR, station)
        if not os.path.isdir(datadir):
            os.makedirs(datadir)
        station4 = station if len(station) == 4 else f"K{station}"
        for page in [5, 6]:
            fn = "640%s0%s%s%02i.dat" % (page, station4, dt.year, dt.month)
            if not os.path.isfile(f"{datadir}/{fn}"):
                uri = f"{baseuri}/640{page}-{dt.strftime('%Y')}/{fn}"
                req = exponential_backoff(requests.get, uri, timeout=60)
                if req is None:
                    LOG.info("total failure %s", uri)
                    continue
                if req.status_code != 200:
                    LOG.info("failed %s %s", uri, req.status_code)
                    continue
                with open(f"{datadir}/{fn}", "wb") as fh:
                    fh.write(req.content)
            df.at[station, f"fn{page}"] = f"{datadir}/{fn}"


def liner(fn):
    """Hacky."""
    return codecs.open(fn, "r", "utf-8", "ignore")


def runner(pgconn, row, station):
    """Do the work prescribed."""
    if not os.path.isfile(row["fn5"]) or not os.path.isfile(row["fn6"]):
        LOG.debug("skipping %s due to missing files", station)
        return 0

    # Our final amount of data
    data = {}
    # We have two files to worry about
    for ln in liner(row["fn5"]):
        d = p1_parser(ln)
        if d is None or d["valid"] <= row["archive_end"]:
            continue
        data[d["valid"]] = d

    for ln in liner(row["fn6"]):
        d = p2_parser(ln)
        if d is None or d["valid"] <= row["archive_end"]:
            continue
        res = data.setdefault(d["valid"], {})
        res.update(d)

    if not data:
        LOG.debug(
            "No data found station: %s, archive_end: %s",
            station,
            row["archive_end"],
        )
        return 0

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

    cursor = pgconn.cursor()
    cursor.execute(
        (
            "DELETE from alldata_1minute WHERE station = '%s' and "
            "valid >= '%s' and valid <= '%s';\n"
        )
        % (station, mints, maxts)
    )
    sio = StringIO()
    cols = [
        "station",
        "valid",
        "vis1_coeff",
        "vis1_nd",
        "vis2_coeff",
        "vis2_nd",
        "drct",
        "sknt",
        "gust_drct",
        "gust_sknt",
        "ptype",
        "precip",
        "pres1",
        "pres2",
        "pres3",
        "tmpf",
        "dwpf",
    ]

    # Loop over the data we got please
    for ts in data:
        entry = data[ts]
        entry["station"] = station
        sio.write("\t".join([str(qc(entry, col)) for col in cols]))
        sio.write("\n")
    sio.seek(0)
    cursor.copy_from(sio, "alldata_1minute", columns=cols, null="null")
    count = cursor.rowcount
    cursor.close()
    pgconn.commit()
    return count


def update_iemprops(ts):
    """db update"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        "UPDATE properties SET propvalue = %s "
        "WHERE propname = 'asos.1min.end'",
        (ts.strftime("%Y-%m-%d"),),
    )
    cursor.close()
    pgconn.commit()


def init_dataframe(argv):
    """Build the processing dataframe."""
    pgconn = get_dbconn("mesosite")
    # ASOS query limit keeps other sites out of result that may have 1min
    df = read_sql(
        "SELECT id from stations t JOIN station_attributes a on "
        "(t.iemid = a.iemid) where a.attr = 'HAS1MIN' and t.network ~* 'ASOS' "
        "ORDER by id ASC",
        pgconn,
        index_col="id",
    )
    df["archive_end"] = utc(1980, 1, 1)
    df["fn5"] = ""
    df["fn6"] = ""
    if len(argv) >= 3:
        if len(argv) == 4:
            LOG.info("Limiting work to station %s", argv[1])
            df = df.loc[[argv[1]]]
            dt = utc(int(argv[2]), int(argv[3]))
        else:
            dt = utc(int(argv[1]), int(argv[2]))
        dl_archive(df, dt)
    else:
        dt = utc() - datetime.timedelta(days=1)
        merge_archive_end(df, dt)
        df["archive_end"] = df["archive_end"].fillna(DT1980)
        dl_realtime(df, dt)
        update_iemprops(dt)

    return df


def merge_archive_end(df, dt):
    """Figure out our archive end times."""
    pgconn = get_dbconn("asos1min")
    df2 = read_sql(
        f"SELECT station, max(valid) from t{dt.strftime('%Y%m')}_1minute "
        "GROUP by station",
        pgconn,
        index_col="station",
    )
    LOG.debug("found %s stations in the archive", len(df2.index))
    df["archive_end"] = df2["max"]


def dl_realtime(df, dt):
    """Download and stage the 'real-time' processing."""
    for page in [1, 2]:
        tmpfn = f"om{page}_{dt.strftime('%Y%m')}.tar.Z"
        uri = f"https://www1.ncdc.noaa.gov/pub/download/hidden/onemin/{tmpfn}"
        res = requests.get(uri, timeout=60, stream=True)
        with open(f"{TMPDIR}/{tmpfn}", "wb") as fh:
            for chunk in res.iter_content(chunk_size=4096):
                if chunk:
                    fh.write(chunk)
        with tarfile.open(f"{TMPDIR}/{tmpfn}", "r:gz") as tar:
            for tarinfo in tar:
                if not tarinfo.isreg():
                    continue
                if not tarinfo.name.startswith("640"):
                    LOG.info("Unknown filename %s", tarinfo.name)
                    continue
                page = tarinfo.name[3]
                station = tarinfo.name[5:9]
                if station[0] == "K":
                    station = station[1:]
                if station not in df.index:
                    LOG.info("Unknown station %s, FIXME!", station)
                    continue
                f = tar.extractfile(tarinfo.name)
                with open(f"{TMPDIR}/{tarinfo.name}", "wb") as fh:
                    fh.write(f.read())
                df.at[station, f"fn{page}"] = f"{TMPDIR}/{tarinfo.name}"


def cleanup(df):
    """Pickup after ourselves."""
    for _station, row in df.iterrows():
        for page in [5, 6]:
            fn = row[f"fn{page}"]
            if not pd.isnull(fn) and fn.startswith(TMPDIR):
                LOG.debug("removing %s", fn)
                os.unlink(fn)


def main(argv):
    """Go Main Go"""
    cronjob = not sys.stdout.isatty()
    # Build a dataframe to do work with
    df = init_dataframe(argv)

    pgconn = get_dbconn("asos1min")
    progress = tqdm(df.index.values, disable=cronjob)
    total = 0
    for station in progress:
        row = df.loc[station]
        progress.set_description(f"{station}")
        total += runner(pgconn, row, station)
    if not cronjob or total < 1e6:
        LOG.info("Ingested %s observations", total)
    cleanup(df)


if __name__ == "__main__":
    main(sys.argv)


def test_parser():
    """test things"""
    p1_examples = open("p1_examples.txt").readlines()
    for i, ex in enumerate(p1_examples):
        res = p1_parser(ex)
        if i == 0:
            assert abs(float(res["vis1_coef"]) - 0.109) < 0.01
        if i == 22:
            assert abs(float(res["drct"]) - 261.0) < 0.01
        if i == 24:
            assert abs(float(res["drct"]) - 305.0) < 0.01
        if i == 26:
            assert res.get("drct") is None
        assert res is not None

    p2_examples = open("p2_examples.txt").readlines()
    for i, ex in enumerate(p2_examples):
        res = p2_parser(ex)
        if i == 0:
            assert abs(res["tmpf"] - 29.0) < 0.01
            assert abs(res["dwpf"] - 23.0) < 0.01
        if i == 19:
            assert abs(res["precip"] - 0.01) < 0.01
        if i == 28:
            assert abs(res["dwpf"] - -2) < 0.01
        assert res is not None
