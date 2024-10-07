"""
Attempt to process the 1 minute archives available from NCEI

NCEI provides monthly tar files for nearly up to the current day here:

https://www.ncei.noaa.gov/pub/download/hidden/onemin/

NCEI generates these at about 1530EDT, so we run a bit after that via crontab
"""

# stdlib
import codecs
import datetime
import os
import re
import subprocess
import sys
import tarfile
from io import StringIO
from typing import Optional

# third party
import click
import httpx
import pandas as pd
from pyiem.database import get_dbconn, get_sqlalchemy_conn
from pyiem.util import exponential_backoff, logger, set_property, utc
from sqlalchemy import text
from tqdm import tqdm

LOG = logger()
pd.set_option("future.no_silent_downcasting", True)
HIDDENURL = "https://www.ncei.noaa.gov/pub/download/hidden/onemin"
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
                INT_RE.match(t) is not None for t in ints[-5:-1]
            ):
                ints = ints[-5:-1]
            # So if that failed, try the first four positions
            elif all(INT_RE.match(t) is not None for t in ints[:4]):
                ints = ints[:4]
            # So if that failed, try the last four positions
            elif len(ints) > 4 and all(
                INT_RE.match(t) is not None for t in ints[-4:]
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
                req = exponential_backoff(httpx.get, uri, timeout=60)
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
    sql = (
        f"copy alldata_1minute({','.join(cols)}) from stdin "
        "with null as 'None'"
    )
    with cursor.copy(sql) as copy:
        copy.write(sio.read())
    count = cursor.rowcount
    cursor.close()
    pgconn.commit()
    return count


def init_dataframes(
    year: Optional[int], month: Optional[int], station: Optional[str]
) -> list:
    """Build the processing dataframe."""
    # ASOS query limit keeps other sites out of result that may have 1min
    # Do a time zone trick to figure out UTC offset 1 is ahead
    with get_sqlalchemy_conn("mesosite") as conn:
        df = pd.read_sql(
            """
            SELECT id,
            case when extract(year from ('2020-01-01 00:00+00' at time zone
            tzname)) = 2019 then 1 else -1 end as utc_direction from
            stations t JOIN station_attributes a on
            (t.iemid = a.iemid) where a.attr = 'HAS1MIN'
            and t.network ~* 'ASOS' ORDER by id ASC
            """,
            conn,
            index_col="id",
        )
    # Set a currently impossible floor for a bounds check.
    df["archive_end"] = DT1980
    df["fn5"] = ""
    df["fn6"] = ""
    dt = utc()
    if year is not None and month is not None:
        dt = utc(year, month)
        if station is not None:
            LOG.info("Limiting work to station %s", station)
            df = df.loc[[station]]
        dl_archive(df, dt)
        return [df]
    res = []
    months = [dt]
    if dt.day < 7:
        months.insert(0, dt - datetime.timedelta(days=9))
    for mdt in months:
        df["archive_end"] = DT1980
        df["fn5"] = ""
        df["fn6"] = ""
        merge_archive_end(df, mdt)
        for page in [1, 2]:
            dl_realtime(df, dt, mdt, page)
        res.append(df.copy())
    set_property("asos.1min.end", dt.strftime("%Y-%m-%d"))

    return res


def merge_archive_end(df, dt):
    """Figure out our archive end times."""
    with get_sqlalchemy_conn("asos1min") as conn:
        df2 = pd.read_sql(
            text(
                f"SELECT station, max(valid) from t{dt:%Y%m}_1minute "
                "GROUP by station"
            ),
            conn,
            index_col="station",
        )
    LOG.info("found %s stations in the archive", len(df2.index))
    df["archive_end"] = df2["max"]
    df["archive_end"] = df["archive_end"].fillna(DT1980).infer_objects()


def dl_realtime(df, dt, mdt, page):
    """Download and stage the 'real-time' processing."""
    # Good grief asos-1min-pg1_d202207_c20220721.tar.gz
    tmpfn = f"asos-1min-pg{page}_d{mdt:%Y%m}_c{dt:%Y%m%d}.tar.gz"
    if not os.path.isfile(f"{TMPDIR}/{tmpfn}"):
        uri = f"{HIDDENURL}/{tmpfn}"
        with httpx.stream("GET", uri, timeout=60) as resp:
            if resp.status_code != 200:
                loglvl = LOG.info if dt.month != mdt.month else LOG.warning
                loglvl("Got HTTP %s for %s", resp.status_code, uri)
                return
            with open(f"{TMPDIR}/{tmpfn}", "wb") as fh:
                for chunk in resp.iter_bytes():
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
    subprocess.call(["tmpwatch", "200", TMPDIR])


@click.command()
@click.option("--year", type=int, required=False, help="Year to process")
@click.option("--month", type=int, required=False, help="Month to process")
@click.option("--station", type=str, required=False, help="Station to process")
def main(year: Optional[int], month: Optional[int], station: Optional[str]):
    """Go Main Go"""
    cronjob = not sys.stdout.isatty()
    # Build a dataframe to do work with
    total = 0
    for df in init_dataframes(year, month, station):
        pgconn = get_dbconn("asos1min")
        progress = tqdm(df.index.values, disable=cronjob)
        for _station in progress:
            row = df.loc[_station]
            progress.set_description(f"{_station}")
            total += runner(pgconn, row, _station)
        pgconn.close()
        cleanup(df)
    LOG.info("Ingested %s observations", total)


if __name__ == "__main__":
    main()


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
