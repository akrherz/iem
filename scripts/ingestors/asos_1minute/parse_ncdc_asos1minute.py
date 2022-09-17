"""
 Attempt to process the 1 minute archives available from NCDC

 NCDC provides monthly tar files for nearly up to the current day here:

 https://www1.ncdc.noaa.gov/pub/download/hidden/onemin/
"""
# stdlib
import re
import codecs
import os
from io import StringIO
import subprocess
import sys
import tarfile
import datetime

# third party
import pandas as pd
from pyiem.util import (
    get_dbconn,
    get_dbconnstr,
    logger,
    utc,
    exponential_backoff,
)
import requests
from tqdm import tqdm

LOG = logger()
HIDDENURL = "https://www1.ncdc.noaa.gov/pub/download/hidden/onemin"
BASEDIR = "/mesonet/ARCHIVE/raw/asos/data"
TMPDIR = "/mesonet/tmp/asos1min"
if not os.path.isdir(TMPDIR):
    os.makedirs(TMPDIR)

REAL_RE = re.compile(r"^\-?\d+\.\d+$")
INT_RE = re.compile(r"^\-?\d+$")
RUNWAY_RE = re.compile(r" \d+\s\d+\+?\s*$")
DT1980 = utc(1980, 1, 1)


def tstamp2dt(s, metadata):
    """Convert a string to a datetime"""
    if s[0] not in ["1", "2"]:
        LOG.debug("bad timestamp |%s|", s)
        return None
    try:
        ts = utc(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except Exception:
        LOG.debug("bad timestamp |%s|", s)
        return None
    local_hr = int(s[8:10])
    utc_hr = int(s[12:14])
    utc_is_ahead = metadata["utc_direction"] == 1
    # PAIN
    if utc_is_ahead and utc_hr < local_hr:
        ts += datetime.timedelta(hours=24)
    elif not utc_is_ahead and utc_hr > local_hr:
        ts -= datetime.timedelta(hours=24)

    return ts.replace(hour=utc_hr, minute=int(s[14:16]))


def p2_parser(ln, metadata):
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
    res["valid"] = tstamp2dt(res["tstamp"], metadata)
    if res["valid"] is None:
        return None
    s = ln[31:34].strip()
    res["ptype"] = None if s == "" else s[:2]
    s = ln[43:48].strip()
    res["precip"] = make_real(s, 0, 0.5)
    s = ln[69:77].strip()
    res["pres1"] = make_real(s, 10, 40)
    s = ln[77:85].strip()
    res["pres2"] = make_real(s, 10, 40)
    s = ln[85:93].strip()
    res["pres3"] = make_real(s, 10, 40)
    s = ln[94:97].strip()
    res["tmpf"] = make_int(s, -90, 150)
    s = ln[99:102].strip()
    res["dwpf"] = make_int(s, -90, 150)

    return res


def make_real(s, minval, maxval):
    """Make an integer, if we can!"""
    if REAL_RE.match(s):
        val = float(s)
        if minval <= val <= maxval:
            return val
        LOG.debug("val %s outside of bounds %s %s", val, minval, maxval)

    return None


def make_int(s, minval, maxval):
    """Make an integer, if we can!"""
    if INT_RE.match(s):
        val = int(s)
        if minval <= val <= maxval:
            return val
        LOG.debug("val %s outside of bounds %s %s", val, minval, maxval)

    return None


def p1_parser(line, metadata):
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
    res["valid"] = tstamp2dt(res["tstamp"], metadata)
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
            res[f"vis{vispos}_coeff"] = make_real(token, 0, 100)
            i += 1
            if len(tokens[i]) == 1 and tokens[i].isalpha():
                res[f"vis{vispos}_nd"] = tokens[i]
                i += 1
            vispos += 1
            continue
        # Once we find an int, we are done with viz work and the pain starts
        if token.isdigit() or token == "M":
            # Get the remainder
            ints = tokens[i:]
            # Ideally, we find 4 ints in a row in the -5 to -2 positions as the
            # last is the runway value
            if len(ints) > 4 and all(
                [INT_RE.match(t) is not None for t in ints[-5:-1]]
            ):
                ints = ints[-5:-1]
            # So if that failed, try the first four positions
            elif all([INT_RE.match(t) is not None for t in ints[:4]]):
                ints = ints[:4]
            # So if that failed, try the last four positions
            elif len(ints) > 4 and all(
                [INT_RE.match(t) is not None for t in ints[-4:]]
            ):
                ints = ints[-4:]
            else:
                ints = []
            break
        i += 1
    if len(ints) >= 4:
        res["drct"] = make_int(ints[0], 0, 360)
        res["sknt"] = make_int(ints[1], 0, 125)
        res["gust_drct"] = make_int(ints[2], 0, 360)
        res["gust_sknt"] = make_int(ints[3], 0, 125)
    return res


def dl_archive(df, dt):
    """Do archived downloading."""
    # https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-
    # minute-pg1/access/2022/08/asos-1min-pg1-K1J0-202208.dat
    baseuri = (
        "https://www.ncei.noaa.gov/data/automated-surface-observing-system-"
        "one-minute-pg"
    )
    for station in df.index.values:
        datadir = f"{BASEDIR}/{station}"
        if not os.path.isdir(datadir):
            os.makedirs(datadir)
        station4 = station if len(station) == 4 else f"K{station}"
        for page in [1, 2]:
            fn = f"asos-1min-pg{page}-{station4}-{dt:%Y%m}.dat"
            if not os.path.isfile(f"{datadir}/{fn}"):
                uri = f"{baseuri}{page}/access/{dt:%Y/%m}/{fn}"
                req = exponential_backoff(requests.get, uri, timeout=60)
                if req is None:
                    LOG.info("total failure %s", uri)
                    continue
                if req.status_code != 200:
                    LOG.info("failed %s %s", uri, req.status_code)
                    continue
                with open(f"{datadir}/{fn}", "wb") as fh:
                    fh.write(req.content)
            df.at[station, f"fn{page + 4}"] = f"{datadir}/{fn}"


def liner(fn):
    """Hacky."""
    return codecs.open(fn, "r", "utf-8", "ignore")


def runner(pgconn, metadata, station):
    """Do the work prescribed."""
    if not os.path.isfile(metadata["fn5"]) or not os.path.isfile(
        metadata["fn6"]
    ):
        return 0

    # Our final amount of data
    data = {}
    # We have two files to worry about
    for ln in liner(metadata["fn5"]):
        d = p1_parser(ln, metadata)
        if d is None or d["valid"] <= metadata["archive_end"]:
            continue
        data[d["valid"]] = d

    for ln in liner(metadata["fn6"]):
        d = p2_parser(ln, metadata)
        if d is None or d["valid"] <= metadata["archive_end"]:
            continue
        res = data.setdefault(d["valid"], {})
        res.update(d)

    if not data:
        LOG.debug(
            "No data found station: %s, archive_end: %s",
            station,
            metadata["archive_end"],
        )
        return 0

    mints = min(data)
    maxts = max(data)
    if (maxts - mints) > datetime.timedelta(days=40):
        LOG.warning(
            "refusing to update %s due to %s-%s > 40 days",
            station,
            mints,
            maxts,
        )
        return 0

    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from alldata_1minute WHERE station = %s and "
        "valid >= %s and valid <= %s",
        (station, mints, maxts),
    )
    LOG.debug(
        "removed %s rows between %s and %s", cursor.rowcount, mints, maxts
    )
    sio = StringIO()
    cols = (
        "station valid vis1_coeff vis1_nd vis2_coeff vis2_nd vis3_coeff "
        "vis3_nd drct sknt gust_drct gust_sknt ptype precip pres1 "
        "pres2 pres3 tmpf dwpf"
    ).split()

    # Loop over the data we got please
    fmt = "\t".join(["%s"] * len(cols[2:]))
    for ts, entry in data.items():
        sio.write(f"{station}\t{ts}\t")
        sio.write(fmt % (*[entry.get(col) for col in cols[2:]],))
        sio.write("\n")
    sio.seek(0)
    cursor.copy_from(sio, "alldata_1minute", columns=cols, null="None")
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
    # ASOS query limit keeps other sites out of result that may have 1min
    # Do a time zone trick to figure out UTC offset 1 is ahead
    df = pd.read_sql(
        "SELECT id, "
        "case when extract(year from ('2020-01-01 00:00+00' at time zone "
        "tzname)) = 2019 then 1 else -1 end as utc_direction from "
        "stations t JOIN station_attributes a on "
        "(t.iemid = a.iemid) where a.attr = 'HAS1MIN' and t.network ~* 'ASOS' "
        "ORDER by id ASC",
        get_dbconnstr("mesosite"),
        index_col="id",
    )
    # Set a currently impossible floor for a bounds check.
    df["archive_end"] = utc(1980, 1, 1)
    df["fn5"] = ""
    df["fn6"] = ""
    dt = utc() - datetime.timedelta(days=2)
    if len(argv) == 2:  # Hard coded hidden filename
        dl_realtime(df, dt, filebase=argv[1])
    elif len(argv) >= 3:
        if len(argv) == 4:
            LOG.info("Limiting work to station %s", argv[1])
            df = df.loc[[argv[1]]]
            dt = utc(int(argv[2]), int(argv[3]))
        else:
            dt = utc(int(argv[1]), int(argv[2]))
        dl_archive(df, dt)
    else:
        merge_archive_end(df, dt)
        df["archive_end"] = df["archive_end"].fillna(DT1980)
        dl_realtime(df, dt)
        update_iemprops(dt)

    return df


def merge_archive_end(df, dt):
    """Figure out our archive end times."""
    df2 = pd.read_sql(
        f"SELECT station, max(valid) from t{dt.strftime('%Y%m')}_1minute "
        "GROUP by station",
        get_dbconnstr("asos1min"),
        index_col="station",
    )
    LOG.debug("found %s stations in the archive", len(df2.index))
    df["archive_end"] = df2["max"]


def dl_realtime(df, dt, filebase=None):
    """Download and stage the 'real-time' processing."""
    for page in [1, 2]:
        # Good grief asos-1min-pg1_d202207_c20220721.tar.gz
        tmpfn = (
            f"asos-1min-pg{page}_d{dt.strftime('%Y%m')}_c{dt:%Y%m%d}.tar.gz"
        )
        if filebase is not None:
            tmpfn = f"asos-1min-pg{page}_{filebase}.tar.gz"
        if not os.path.isfile(f"{TMPDIR}/{tmpfn}"):
            uri = f"{HIDDENURL}/{tmpfn}"
            res = requests.get(uri, timeout=60, stream=True)
            if res.status_code != 200:
                LOG.warning("Got HTTP %s for %s", res.status_code, uri)
                continue
            with open(f"{TMPDIR}/{tmpfn}", "wb") as fh:
                for chunk in res.iter_content(chunk_size=4096):
                    if chunk:
                        fh.write(chunk)
        with tarfile.open(f"{TMPDIR}/{tmpfn}", "r:gz") as tar:
            for tarinfo in tar:
                if not tarinfo.isreg():
                    continue
                if not tarinfo.name.startswith("asos-1min-pg"):
                    LOG.info("Unknown filename %s", tarinfo.name)
                    continue
                station = tarinfo.name.split("-")[3]
                if station[0] == "K":
                    station = station[1:]
                if station not in df.index:
                    LOG.warning("Unknown station %s, FIXME!", station)
                    continue
                f = tar.extractfile(tarinfo.name)
                with open(f"{TMPDIR}/{tarinfo.name}", "wb") as fh:
                    fh.write(f.read())
                # sick
                df.at[station, f"fn{page + 4}"] = f"{TMPDIR}/{tarinfo.name}"


def cleanup(df):
    """Pickup after ourselves."""
    for _station, row in df.iterrows():
        for page in [5, 6]:
            fn = row[f"fn{page}"]
            if not pd.isnull(fn) and fn.startswith(TMPDIR):
                os.unlink(fn)
    # Cleanup tmp folder
    subprocess.call(f"tmpwatch 200 {TMPDIR}", shell=True)


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


def test_timestamp():
    """Test that coversion of timestamps."""
    res = tstamp2dt("2001100100021402", {"utc_direction": -1})
    assert res == utc(2001, 9, 30, 14, 2)
    res = tstamp2dt("2001100110000000", {"utc_direction": -1})
    assert res == utc(2001, 10, 1)
    res = tstamp2dt("2001100100000600", {"utc_direction": 1})
    assert res == utc(2001, 10, 1, 6)
    res = tstamp2dt("2001100123000500", {"utc_direction": 1})
    assert res == utc(2001, 10, 2, 5)


def test_parser():
    """test things"""
    metadata = {"utc_direction": 1}
    with open("p1_examples.txt", encoding="utf-8") as fh:
        p1_examples = fh.readlines()
    for i, ex in enumerate(p1_examples):
        res = p1_parser(ex, metadata)
        if i == 0:
            assert abs(float(res["vis1_coeff"]) - 0.109) < 0.01
        if i == 22:
            assert abs(float(res["drct"]) - 261.0) < 0.01
        if i == 24:
            assert abs(float(res["drct"]) - 305.0) < 0.01
        if i in [26, 27]:
            assert res.get("drct") is None
        assert res is not None
    with open("p2_examples.txt", encoding="utf-8") as fh:
        p2_examples = fh.readlines()
    for i, ex in enumerate(p2_examples):
        res = p2_parser(ex, metadata)
        if i == 0:
            assert abs(res["tmpf"] - 29.0) < 0.01
            assert abs(res["dwpf"] - 23.0) < 0.01
        if i == 19:
            assert abs(res["precip"] - 0.01) < 0.01
        if i == 29:
            assert abs(res["precip"] - 0.03) < 0.01
        if i == 28:
            assert abs(res["dwpf"] - -2) < 0.01
        assert res is not None
