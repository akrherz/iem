"""Ingest the PRISM data into a local yearly netCDF file

Called from RUN_NOON.sh and RUN_2AM.sh
"""
import datetime
import glob
import os
import subprocess
import sys

import numpy as np
import rasterio
from pyiem.iemre import daily_offset
from pyiem.util import get_dbconn, get_properties, logger, ncopen

LOG = logger()
PROPNAME = "prism.archive_end"


def do_process(valid, fn):
    """Process this file, please"""
    # shape of data is (1, 621, 1405)
    LOG.info("Processing %s", fn)
    data = rasterio.open(fn).read()
    varname = fn.split("_")[1]
    idx = daily_offset(valid)
    with ncopen(f"/mesonet/data/prism/{valid.year}_daily.nc", "a") as nc:
        nc.variables[varname][idx] = np.flipud(data[0])


def do_download(valid):
    """Make the download happen!"""
    files = []
    for varname in ["ppt", "tmax", "tmin"]:
        d = "2"  # if varname == "ppt" else "1"
        for classify in ["stable", "provisional", "early"]:
            localfn = valid.strftime(
                f"PRISM_{varname}_{classify}_4kmD{d}_%Y%m%d_bil"
            )
            for fn in glob.glob("{localfn}*"):
                os.unlink(fn)

            uri = valid.strftime(
                f"ftp://prism.nacse.org/daily/{varname}/%Y/{localfn}.zip"
            )
            subprocess.call(
                [
                    "wget",
                    "-q",
                    "--timeout=120",
                    "-O",
                    f"{localfn}.zip",
                    uri,
                ],
            )
            # a failed download is a 0-byte file :/
            if os.stat(f"{localfn}.zip").st_size == 0:
                os.unlink(f"{localfn}.zip")
                continue
            LOG.info("Worked %s", localfn)
            break

        subprocess.call(["unzip", "-q", f"{localfn}.zip"])
        files.append(f"{localfn}.bil")

    return files


def do_cleanup(valid):
    """do cleanup"""
    subprocess.call(
        "rm -f PRISM*%s*" % (valid.strftime("%Y%m%d"),), shell=True
    )


def update_properties(valid):
    """Conditionally update the database flag for when PRISM ends."""
    props = get_properties()
    current = datetime.datetime.strptime(
        props.get(PROPNAME, "1980-01-01"),
        "%Y-%m-%d",
    ).date()
    if current > valid:
        return
    with get_dbconn("mesosite") as dbconn:
        cursor = dbconn.cursor()
        args = (valid.strftime("%Y-%m-%d"), PROPNAME)
        LOG.info("setting %s", args)
        cursor.execute(
            "UPDATE properties SET propvalue = %s where propname = %s",
            args,
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT into properties(propvalue, propname) VALUES (%s, %s)",
                args,
            )
        cursor.close()
        dbconn.commit()


def main(argv):
    """Do Something"""
    os.chdir("/mesonet/tmp")
    valid = datetime.date(int(argv[1]), int(argv[2]), int(argv[3]))
    files = do_download(valid)
    for fn in files:
        do_process(valid, fn)

    do_cleanup(valid)
    update_properties(valid)


if __name__ == "__main__":
    main(sys.argv)
