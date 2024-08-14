"""Ingest the PRISM data into a local yearly netCDF file

RUN_2AM.sh for 7,60,365 days ago
RUN_NOON.sh for 1 day ago
"""

import datetime
import glob
import os
import subprocess

import click
import numpy as np
import rasterio
from pyiem.iemre import daily_offset
from pyiem.util import get_properties, logger, ncopen, set_property

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
    for fn in glob.glob(f"PRISM*{valid:%Y%m%d}*"):
        os.unlink(fn)


def update_properties(valid):
    """Conditionally update the database flag for when PRISM ends."""
    props = get_properties()
    current = datetime.datetime.strptime(
        props.get(PROPNAME, "1980-01-01"),
        "%Y-%m-%d",
    ).date()
    if current > valid:
        return
    set_property(PROPNAME, valid.strftime("%Y-%m-%d"))


@click.command()
@click.option(
    "--date", "dt", type=click.DateTime(), required=True, help="Date"
)
def main(dt: datetime.datetime):
    """Do Something"""
    os.chdir("/mesonet/tmp")
    dt = dt.date()
    files = do_download(dt)
    for fn in files:
        do_process(dt, fn)

    do_cleanup(dt)
    update_properties(dt)


if __name__ == "__main__":
    main()
