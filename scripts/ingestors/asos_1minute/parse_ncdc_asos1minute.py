"""
 Attempt to process the 1 minute archives available from NCDC

 NCDC provides monthly tar files for nearly up to the current day here:

 https://www1.ncdc.noaa.gov/pub/download/hidden/onemin/
"""
import re
import os
import subprocess
import sys
import datetime

import pytz
from pyiem.util import get_dbconn, logger
import requests
from tqdm import tqdm

LOG = logger()
BASEDIR = "/mesonet/ARCHIVE/raw/asos/"

P1_RE = re.compile(
    r"""
(?P<wban>[0-9]{5})
(?P<faaid>[0-9A-Z]{4})\s
(?P<id3>[0-9A-Z]{3})
(?P<tstamp>[0-9]{16})\s+
((?P<vis1_coef>\-?\d+\.\d*)|(?P<vis1_coef_miss>M))\s*\s*
(?P<vis1_nd>[0-9A-Za-z\?\$/ ])\s+
((?P<vis2_coef>\d+\.\d*)|(?P<vis2_coef_miss>[M ]))\s+
(?P<vis2_nd>[A-Za-z\?\$ ])\s+
..............\s+
((?P<drct>\d+)|(?P<drct_miss>M))\s+
((?P<sknt>\d+)|(?P<sknt_miss>M))\s+
((?P<gust_drct>\d+)\+?|(?P<gust_drct_miss>M))\s+
((?P<gust_sknt>\d+)C?R?L?F*\d*\+?|(?P<gust_sknt_miss>M))\s+
(....)\s
(...)
""",
    re.VERBOSE,
)

p1_examples = open("p1_examples.txt").readlines()

P2_RE = re.compile(
    r"""
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
""",
    re.VERBOSE,
)


p2_examples = open("p2_examples.txt").readlines()


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
    res["ts"] = tstamp2dt(res["tstamp"])
    return res


def p1_parser(ln):
    """
    Handle the parsing of a line found in the 6505 report, return QC dict
    """
    # Some rectification
    if ln[30:65].strip() == "":
        ln = "%s  M  M         M   M               %s" % (ln[:30], ln[65:])
    m = P1_RE.match(ln.replace("]", "").replace("[", ""))
    if m is None:
        print("P1_FAIL:|%s|" % (ln,))
        return None
    res = m.groupdict()
    res["ts"] = tstamp2dt(res["tstamp"])
    return res


def download(station, monthts):
    """
    Download a month file from NCDC
    """
    station4 = station if len(station) == 4 else f"K{station}"
    baseuri = "https://www1.ncdc.noaa.gov/pub/data/asos-onemin/"
    datadir = "%s/data/%s" % (BASEDIR, station)
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
    for page in [5, 6]:
        uri = baseuri + "640%s-%s/640%s0%s%s.dat" % (
            page,
            monthts.year,
            page,
            station4,
            monthts.strftime("%Y%m"),
        )
        req = requests.get(uri)
        if req.status_code != 200:
            LOG.info("dl %s failed with code %s", uri, req.status_code)
            continue
        with open(
            "%s/640%s0%s%s.dat"
            % (datadir, page, station4, monthts.strftime("%Y%m")),
            "wb",
        ) as fp:
            fp.write(req.content)


def runner(station, monthts):
    """
    Parse a month's worth of data please
    """
    station4 = station if len(station) == 4 else f"K{station}"

    # Our final amount of data
    data = {}
    if os.path.isfile(
        "64050%s%s%02i" % (station4, monthts.year, monthts.month)
    ):
        fn5 = "64050%s%s%02i" % (station4, monthts.year, monthts.month)
        fn6 = "64060%s%s%02i" % (station4, monthts.year, monthts.month)
    else:
        fn5 = ("%sdata/%s/64050%s%s%02i.dat") % (
            BASEDIR,
            station,
            station4,
            monthts.year,
            monthts.month,
        )
        fn6 = ("%sdata/%s/64060%s%s%02i.dat") % (
            BASEDIR,
            station,
            station4,
            monthts.year,
            monthts.month,
        )
        if not os.path.isfile(fn5):
            try:
                download(station, monthts)
            except Exception as exp:
                print("download() error %s" % (exp,))
            if not os.path.isfile(fn5) or not os.path.isfile(fn6):
                print(
                    ("NCDC did not have %s station for %s")
                    % (station, monthts.strftime("%b %Y"))
                )
                return
    # We have two files to worry about
    for ln in open(fn5):
        d = p1_parser(ln)
        if d is None:
            continue
        data[d["ts"]] = d

    for ln in open(fn6):
        d = p2_parser(ln)
        if d is None:
            continue
        if d["ts"] not in data:
            data[d["ts"]] = {}
        for k in d.keys():
            data[d["ts"]][k] = d[k]

    if not data:
        print("No data found for station: %s" % (station,))
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
    out = open(tmpfn, "w")
    out.write(
        """DELETE from alldata_1minute WHERE station = '%s' and
               valid >= '%s' and valid <= '%s';\n"""
        % (station, mints, maxts)
    )
    out.write("COPY alldata_1minute FROM stdin WITH NULL as 'Null';\n")

    # Loop over the data we got please
    keys = list(data.keys())
    keys.sort()
    flipped = False
    for ts in keys:
        if ts.year != monthts.year and not flipped:
            print("  Flipped years from %s to %s" % (monthts.year, ts.year))
            out.write("\\.\n")
            out.write("COPY alldata_1minute FROM stdin WITH NULL as 'Null';\n")
            flipped = True
        ln = ""
        data[ts]["station"] = station
        for col in [
            "station",
            "ts",
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
        ]:
            ln += "%s\t" % (data[ts].get(col) or "Null",)
        out.write(ln[:-1] + "\n")
    out.write("\\.\n")
    out.close()

    proc = subprocess.Popen(
        "psql -f %s -h iemdb-asos.local asos" % (tmpfn,),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = proc.stdout.read().decode("utf-8")
    stderr = proc.stderr.read().decode("utf-8")

    print(
        (
            "%s %s processed %s entries [%s to %s UTC]\n"
            "STDOUT: %s\nSTDERR: %s"
        )
        % (
            datetime.datetime.now().strftime("%H:%M %p"),
            station,
            len(data.keys()),
            mints.strftime("%y%m%d %H:%M"),
            maxts.strftime("%y%m%d %H:%M"),
            stdout.replace("\n", " "),
            stderr.replace("\n", " "),
        )
    )

    os.unlink(tmpfn)


def update_iemprops():
    """db update"""
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    m1 = datetime.date.today().replace(day=1)
    cursor.execute(
        """
        UPDATE properties SET propvalue = %s
        WHERE propname = 'asos.1min.end'
    """,
        (m1.strftime("%Y-%m-%d"),),
    )
    cursor.close()
    pgconn.commit()


def get_stations():
    """Figure out which stations we need to process."""
    cursor = get_dbconn("mesosite").cursor()
    res = []
    cursor.execute(
        "SELECT id from stations t JOIN station_attributes a on "
        "(t.iemid = a.iemid) where a.attr = 'HAS1MIN' and t.network ~* 'ASOS'"
    )
    for row in cursor:
        res.append(row[0])
    return res


def main(argv):
    """Go Main Go"""
    stations = get_stations()
    dates = []
    if len(argv) == 3:
        dates.append(datetime.datetime(int(argv[1]), int(argv[2]), 1))
    elif len(argv) == 4:
        stations = [sys.argv[1]]
        if int(argv[3]) != 0:
            months = [int(argv[3])]
        else:
            months = range(1, 13)
        for month in months:
            dates.append(datetime.datetime(int(argv[2]), month, 1))
    else:
        # default to last month
        ts = datetime.date.today() - datetime.timedelta(days=19)
        dates.append(datetime.datetime(ts.year, ts.month, 1))
        update_iemprops()

    progress = tqdm(stations, disable=not sys.stdout.isatty())
    for station in progress:
        for date in dates:
            progress.set_description(f"{station} {date.strftime('%Y%m')}")
            try:
                runner(station, date)
            except Exception as exp:
                LOG.info("uncaught exception parsing %s %s", station, date)
                LOG.exception(exp)


if __name__ == "__main__":
    main(sys.argv)


def test_parser():
    """test things"""
    for i, ex in enumerate(p1_examples):
        res = p1_parser(ex)
        if i == 0:
            assert abs(float(res["vis1_coef"]) - 0.109) < 0.01
        if i == 22:
            assert abs(float(res["drct"]) - 155.0) < 0.01
        assert res is not None

    for ex in p2_examples:
        res = p2_parser(ex)
        assert res is not None
