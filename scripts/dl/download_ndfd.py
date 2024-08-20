"""Fetch the NDFD from the NWS server as CONDUIT is down again.

Currently, the CONDUIT writer does:

TMPK|DWPK|SPED|DRCT|APCP06|P06M|TMXK12|TMNK12|WBGT

Run from RUN_50_AFTER and RUN_10_AFTER
"""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import httpx
import pygrib
from pyiem.util import archive_fetch, logger

LOG = logger()
SERVER = (
    "https://tgftp.nws.noaa.gov/SL.us008001/ST.opnl/DF.gr2/DC.ndfd/AR.conus"
)


def process_grib(grb):
    """Figure out if we need to save this or not."""
    dlname = str(grb)
    tokens = dlname.strip().split(":")
    fstr = tokens[-2].split()[2].split()[0]
    LOG.info("Processing `%s` fstr: %s", dlname, fstr)
    if fstr.find("-") > -1:
        f1, f2 = fstr.split("-")
    else:
        f1 = "0"
        f2 = fstr
    runtime = datetime.strptime(tokens[-1][-12:], "%Y%m%d%H%M").replace(
        tzinfo=timezone.utc
    )
    if runtime.minute != 0:
        LOG.info("Skipping %s as it is not a top of the hour", dlname)
        return
    if f1.endswith("m"):
        f1 = runtime + timedelta(minutes=int(f1[:-1]))
    else:
        f1 = runtime + timedelta(hours=int(f1))
    if f2.endswith("m"):
        f2 = runtime + timedelta(minutes=int(f2[:-1]))
    else:
        f2 = runtime + timedelta(hours=int(f2))
    LOG.info("Found %s -> %s %s", str(grb), f1, f2)
    # compute the archive filename
    fhour = int((f2 - runtime).total_seconds() / 3600)
    ppath = (
        f"{runtime:%Y/%m/%d}/model/ndfd/{runtime:%H}/ndfd.t{runtime:%H}z."
        f"awp2p5f{fhour:03.0f}.grib2"
    )
    with archive_fetch(ppath) as fn:
        if fn is not None:
            with pygrib.open(fn) as grbs:
                for grb2 in grbs:
                    if grb2.parameterName == grb.parameterName:
                        LOG.info(
                            "Skipping %s as we have it in archive already",
                            str(grb),
                        )
                        return
    with open("sendme.grb", "wb") as fh:
        fh.write(grb.tostring())
    pqstr = f"data u {runtime:%Y%m%d%H%M} bogus {ppath[11:]} grib2"
    cmd = [
        "pqinsert",
        "-p",
        pqstr,
        "sendme.grb",
    ]
    LOG.info("Running: %s", " ".join(cmd))
    subprocess.call(cmd)


def workflow(url):
    """Fetch the URL, see what we have."""
    try:
        with httpx.stream("GET", url) as resp:
            with open("data.bin", "wb") as fh:
                for chunk in resp.iter_bytes():
                    fh.write(chunk)
    except Exception as exp:
        LOG.info("download_ndfd failed to fetch %s: %s", url, exp)
        return
    with pygrib.open("data.bin") as grbs:
        for grb in grbs:
            process_grib(grb)


def main():
    """Go Main Go."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for period in ["001-003", "004-007"]:
            for vname in "maxt mint wbgt temp td wdir qpf wspd".split():
                if vname == "qpf" and period == "004-007":
                    continue
                url = f"{SERVER}/VP.{period}/ds.{vname}.bin"
                workflow(url)


if __name__ == "__main__":
    main()
