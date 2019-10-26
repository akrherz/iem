"""Get some soil grids from the NAM"""
from __future__ import print_function
import subprocess
import sys
import datetime
import os

import requests
import pygrib
from pyiem.util import exponential_backoff


def need_to_run(valid, hr):
    """ Check to see if we already have the radiation data we need"""
    gribfn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/nam/"
            "%H/nam.t%Hz.conusnest.hiresf0" + str(hr) + ".tm00.grib2"
        )
    )
    if not os.path.isfile(gribfn):
        return True
    try:
        grbs = pygrib.open(gribfn)
        if grbs.messages < 5:
            return True
    except Exception:
        return True
    return False


def fetch(valid, hr):
    """ Fetch the data for this timestamp
    """
    uri = valid.strftime(
        (
            "http://www.ftp.ncep.noaa.gov/data/nccf/"
            "com/nam/prod/nam.%Y%m%d/nam.t%Hz.conusnest."
            "hiresf0" + str(hr) + ".tm00.grib2.idx"
        )
    )
    req = exponential_backoff(requests.get, uri, timeout=30)
    if req is None or req.status_code != 200:
        print("download_hrrr failed to get idx\n%s" % (uri,))
        return

    offsets = []
    neednext = False
    for line in req.content.decode("utf-8").split("\n"):
        tokens = line.split(":")
        if len(tokens) < 3:
            continue
        if neednext:
            offsets[-1].append(int(tokens[1]))
            neednext = False
        if tokens[3] in ["ULWRF", "DSWRF"]:
            if tokens[4] == "surface" and tokens[5].find("ave fcst") > 0:
                offsets.append([int(tokens[1])])
                neednext = True
        # Save soil temp and water at surface, 10cm and 40cm
        if tokens[3] in ["TSOIL", "SOILW"]:
            if tokens[4] in [
                "0-0.1 m below ground",
                "0.1-0.4 m below ground",
                "0.4-1 m below ground",
            ]:
                offsets.append([int(tokens[1])])
                neednext = True

    outfn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/nam/"
            "%H/nam.t%Hz.conusnest.hiresf0" + str(hr) + ".tm00.grib2"
        )
    )
    outdir = os.path.dirname(outfn)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)  # make sure LDM can then write to dir
        subprocess.call("chmod 775 %s" % (outdir,), shell=True)
    output = open(outfn, "ab", 0o664)

    if len(offsets) != 8:
        print(
            "download_nam warning, found %s gribs for %s[%s]"
            % (len(offsets), valid, hr)
        )
    for pr in offsets:
        headers = {"Range": "bytes=%s-%s" % (pr[0], pr[1])}
        req = exponential_backoff(requests.get, uri[:-4], headers=headers, timeout=30)
        if req is None:
            print("download_nam.py failure for uri: %s" % (uri,))
        else:
            output.write(req.content)

    output.close()


def main():
    """ Go Main Go"""
    ts = datetime.datetime(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
    # script is called every hour, just short circuit the un-needed hours
    if ts.hour % 6 != 0:
        return
    times = [ts]
    times.append(ts - datetime.timedelta(hours=6))
    times.append(ts - datetime.timedelta(hours=24))
    for ts in times:
        for hr in range(6):
            if not need_to_run(ts, hr):
                continue
            fetch(ts, hr)


if __name__ == "__main__":
    os.umask(0o002)
    main()
