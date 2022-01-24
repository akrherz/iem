"""Generate SWAT realtime files workflow.

See akrherz/iem#285.

Run from RUN_2AM.sh
"""
# stdlib
from datetime import date, timedelta
import os
import subprocess
import sys

# third party
from affine import Affine
import numpy as np
import pandas as pd
from geopandas import read_postgis
from pyiem.grid.zs import CachingZonalStats
from pyiem import mrms, iemre
from pyiem.util import get_dbconnstr, logger, ncopen, convert_value
from tqdm import tqdm

LOG = logger()
WORKDIR = "/mesonet/tmp/umrb_swat_realtime"


def init_fps(huc12s):
    """Generate file handles."""
    for huc12 in huc12s.index.values:
        tfp = open(
            os.path.join(WORKDIR, "temperature", f"T{huc12}.txt"),
            "a",
            encoding="utf-8",
        )
        pfp = open(
            os.path.join(WORKDIR, "precipitation", f"P{huc12}.txt"),
            "a",
            encoding="utf-8",
        )
        yield [tfp, pfp]


def init_files(huc12s, now):
    """Create a bunch of files and fps."""
    for huc12 in huc12s.index.values:
        tfp = open(
            os.path.join(WORKDIR, "temperature", f"T{huc12}.txt"),
            "w",
            encoding="utf-8",
        )
        pfp = open(
            os.path.join(WORKDIR, "precipitation", f"P{huc12}.txt"),
            "w",
            encoding="utf-8",
        )
        tfp.write(f"{now:%Y%m%d}\n")
        pfp.write(f"{now:%Y%m%d}\n")
        yield [tfp, pfp]


def workflow(huc12s):
    """Generate the files as we need."""
    # default time domain, only run for one date if the files exist.
    now = date(2019, 1, 1)
    ets = date.today() - timedelta(days=1)
    mrmsaffine = Affine(0.01, 0.0, mrms.WEST, 0.0, -0.01, mrms.NORTH)
    mrms_czs = CachingZonalStats(
        mrmsaffine,
    )
    iemreaffine = Affine(
        iemre.DX, 0.0, iemre.WEST, 0.0, 0 - iemre.DY, iemre.NORTH
    )
    iemre_czs = CachingZonalStats(
        iemreaffine,
    )
    if os.listdir(os.path.join(WORKDIR, "temperature")):
        now = ets
    LOG.info("Running for time domain %s to %s", now, ets)
    mrms_nchandles = {}
    iemre_nchandles = {}
    # Gonna be opening 10k files here...
    swathandles = []
    dates = pd.date_range(now, ets)
    progress = tqdm(dates, disable=not sys.stdout.isatty())
    for now in progress:
        progress.set_description(f"{now:%Y%m%d}")
        offset = iemre.daily_offset(now)
        if now.strftime("%Y%m%d") == "20190101":
            LOG.info("Generating new files")
            swathandles.extend(init_files(huc12s, now))
        elif not swathandles:
            swathandles.extend(init_fps(huc12s))
        # get mrms netcdf handle
        if now.year not in mrms_nchandles:
            mrms_nchandles[now.year] = ncopen(
                iemre.get_daily_mrms_ncname(now.year), "r"
            )
        # get iemre netcdf handle
        if now.year not in iemre_nchandles:
            iemre_nchandles[now.year] = ncopen(
                iemre.get_daily_ncname(now.year), "r"
            )
        # mrms precip
        precip = np.flipud(mrms_nchandles[now.year]["p01d"][offset])
        pdata = mrms_czs.gen_stats(precip, huc12s["simple_geom"])
        # IEMRE high and low
        highk = np.flipud(iemre_nchandles[now.year]["high_tmpk"][offset])
        hdata = convert_value(
            iemre_czs.gen_stats(highk, huc12s["simple_geom"]), "degK", "degC"
        )
        lowk = np.flipud(iemre_nchandles[now.year]["low_tmpk"][offset])
        ldata = convert_value(
            iemre_czs.gen_stats(lowk, huc12s["simple_geom"]), "degK", "degC"
        )
        for i, (p, h, l) in enumerate(zip(pdata, hdata, ldata)):
            swathandles[i][0].write(f"{h:.2f},{l:.2f}\n")
            swathandles[i][1].write(f"{p:.1f}\n")

    for swath in swathandles:
        swath[0].close()
        swath[1].close()


def main():
    """Do things."""
    # 1. Create the work directory
    for subdir in ("temperature", "precipitation"):
        os.makedirs(os.path.join(WORKDIR, subdir), exist_ok=True)
    # 2. Load up HUC12 geometries
    huc12s = read_postgis(
        "SELECT simple_geom, huc12 from wbd_huc12 where umrb_realtime_swat",
        get_dbconnstr("idep"),
        geom_col="simple_geom",
        index_col="huc12",
    )
    LOG.info("Loaded %s HUC12s", len(huc12s.index))

    # 3. Iterate over what we need to iterate over
    workflow(huc12s)
    # 4. Zip up the files
    os.chdir(WORKDIR)
    yesterday = date.today() - timedelta(days=1)
    zipfn = f"umrb_realtime_{yesterday:%Y%m%d}.zip"
    subprocess.call(["zip", "-q", "-r", zipfn, "temperature", "precipitation"])
    # 5. Copy the zip file to the resulting folder
    subprocess.call(
        ["mv", zipfn, "/mesonet/share/pickup/swat/umrb_realtime/"],
    )


if __name__ == "__main__":
    main()
