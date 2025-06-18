"""Generate SWAT realtime files workflow.

See akrherz/iem#285.

We are generating the format directly used by the distrubuted SWAT. Notes:

- 1800 HUCs per file, we generate four total files to cover the 5729 HUC12s
- While the SWATID column is unique, the HUC12 column is not.

Run from RUN_2AM.sh
"""

# stdlib
import glob
import os
import subprocess
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

# third party
from geopandas import read_postgis
from pyiem.database import get_sqlalchemy_conn
from pyiem.grid import nav
from pyiem.grid.zs import CachingZonalStats
from pyiem.iemre import daily_offset, get_daily_mrms_ncname, get_daily_ncname
from pyiem.util import convert_value, logger, ncopen
from tqdm import tqdm

LOG = logger()
WORKDIR = "/mesonet/tmp/umrb_swat_realtime"
DATADIR = "/mesonet/share/pickup/swat/umrb_realtime"


def init_files(page, huc12s):
    """Create a bunch of files and fps."""
    for typ in ["pcp", "tmp"]:
        fn = os.path.join(WORKDIR, f"{typ}{page}.{typ}")
        with open(fn, "w", encoding="utf-8") as fh:
            # Line one has all the SWATIDs
            fh.write("       ")
            minv = huc12s["swat"].min()
            maxv = huc12s["swat"].max()
            assert ((maxv - minv) + 1) == len(huc12s.index)
            fh.writelines(f"{i:>5}" for i in range(minv, maxv + 1))
            fh.write("\n")
            # two empty lines
            fh.write("\n\n")
            # 0 eelvation
            fh.write("Elev   ")
            fh.writelines(f"{0:>5}" for _i in range(minv, maxv + 1))
            fh.write("\n")


def workflow(page, huc12s):
    """Generate the files as we need."""
    if not os.path.isfile(os.path.join(WORKDIR, f"tmp{page}.tmp")):
        init_files(page, huc12s)
        now = date(2019, 1, 1)
    else:
        now = date.today() - timedelta(days=1)
    # default time domain, only run for one date if the files exist.
    ets = date.today() - timedelta(days=1)
    LOG.info("Running for time domain %s to %s", now, ets)
    # This is N to S
    mrms_czs = CachingZonalStats(nav.MRMS_IEMRE.affine_image)
    iemre_czs = CachingZonalStats(nav.IEMRE.affine_image)

    mrms_nchandles = {}
    iemre_nchandles = {}
    dates = pd.date_range(now, ets)
    progress = tqdm(dates, disable=not sys.stdout.isatty())
    # Open our output page files
    tmpfn = os.path.join(WORKDIR, f"tmp{page}.tmp")
    pcpfn = os.path.join(WORKDIR, f"pcp{page}.pcp")
    with (
        open(tmpfn, "a", encoding="utf-8") as tfh,
        open(pcpfn, "a", encoding="utf-8") as pfh,
    ):
        for now in progress:
            progress.set_description(f"{now:%Y%m%d}")
            offset = daily_offset(now)
            # get mrms netcdf handle
            if now.year not in mrms_nchandles:
                mrms_nchandles[now.year] = ncopen(
                    get_daily_mrms_ncname(now.year), "r"
                )
            # get iemre netcdf handle
            if now.year not in iemre_nchandles:
                iemre_nchandles[now.year] = ncopen(
                    get_daily_ncname(now.year), "r"
                )
            # mrms precip
            precip = np.flipud(mrms_nchandles[now.year]["p01d"][offset])
            pdata = mrms_czs.gen_stats(precip, huc12s["simple_geom"])
            # IEMRE high and low
            highk = np.flipud(iemre_nchandles[now.year]["high_tmpk"][offset])
            hdata = convert_value(
                iemre_czs.gen_stats(highk, huc12s["simple_geom"]),
                "degK",
                "degC",
            )
            lowk = np.flipud(iemre_nchandles[now.year]["low_tmpk"][offset])
            ldata = convert_value(
                iemre_czs.gen_stats(lowk, huc12s["simple_geom"]),
                "degK",
                "degC",
            )
            # write the year, date
            tfh.write(f"{now.year:>4}{int(now.strftime('%j')):>3}")
            pfh.write(f"{now.year:>4}{int(now.strftime('%j')):>3}")
            for p, h, ll in zip(pdata, hdata, ldata, strict=False):
                pfh.write(f"{p:5.1f}")
                tfh.write(f"{h:5.1f}{ll:5.1f}")
            tfh.write("\n")
            pfh.write("\n")


def main():
    """Do things."""
    # Load the cross reference
    xref = pd.read_csv(
        os.path.join(DATADIR, "xref.csv"),
        dtype={"huc12": str},
    )
    # Load up HUC12 geometries
    with get_sqlalchemy_conn("idep") as conn:
        huc12s = read_postgis(
            "SELECT simple_geom, huc12 from wbd_huc12 "
            "where umrb_realtime_swat",
            conn,
            geom_col="simple_geom",
            index_col=None,
        )
    # The xref HUC12s are not unique, so we need to do a join
    huc12s = pd.merge(xref, huc12s, how="left", on="huc12")
    huc12s["page"] = huc12s["swat"] // 1800 + 1
    # Need to order by the id
    huc12s = huc12s.sort_values("swat", ascending=True)
    LOG.info("Loaded %s HUC12s", len(huc12s.index))
    # Loop over the pages
    for page, df in huc12s.groupby("page"):
        workflow(page, df)
    # 4. Zip up the files
    os.chdir(WORKDIR)
    yesterday = date.today() - timedelta(days=1)
    zipfn = f"umrb_realtime_{yesterday:%Y%m%d}.zip"
    tfiles = glob.glob("tmp?.tmp")
    pfiles = glob.glob("pcp?.pcp")
    subprocess.call(["zip", "-q", zipfn, *tfiles, *pfiles])
    # 5. Copy the zip file to the resulting folder
    subprocess.call(["mv", zipfn, DATADIR])


if __name__ == "__main__":
    main()
