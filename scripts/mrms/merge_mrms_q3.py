"""Merge the 0.01x0.01 Q3 24 hour precip data estimates.

called from RUN_10_AFTER.sh
"""

import gzip
import os
import tempfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
import netCDF4
import numpy as np
import pygrib
from pyiem.iemre import daily_offset, get_daily_mrms_ncname
from pyiem.mrms import fetch as mrms_fetch
from pyiem.util import logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"

# MultiSensor_QPE_01H_Pass2 after, GaugeCorr_QPE_01H before
PRODFLIP = utc(2020, 10, 13, 19)


def run(nc: netCDF4.Dataset, dt: date, for_dep: bool):
    """Update netcdf file with the MRMS data

    Args:
      dt (date): date to process
      for_dep (bool): for Daily Erosion Project
    """
    offset = daily_offset(dt)
    if for_dep:
        offset = offset - daily_offset(date(dt.year, 4, 11))
    ncprecip = nc.variables["p01d"]

    midnight = datetime(
        dt.year, dt.month, dt.day, tzinfo=ZoneInfo("America/Chicago")
    )
    utcnow = utc()
    total = None
    UTC = ZoneInfo("UTC")
    # Stop at 6 PM if we are using DEP
    for hr in range(1, 18 if for_dep else 25):
        utcdt = (midnight + timedelta(hours=hr)).astimezone(UTC)
        if utcdt > utcnow:
            continue
        gribfn = None
        qcprod = "MultiSensor_QPE_01H_Pass2"
        if utcdt < PRODFLIP:
            qcprod = "GaugeCorr_QPE_01H"
        for prefix in [qcprod, "RadarOnly_QPE_01H"]:
            fn = mrms_fetch(prefix, utcdt)
            if fn is None:
                continue
            LOG.info("Processing %s %s", utcdt, prefix)
            (_, gribfn) = tempfile.mkstemp()
            with gzip.GzipFile(fn, "rb") as zfn, open(gribfn, "wb") as tmpfp:
                tmpfp.write(zfn.read())
            os.unlink(fn)
            break
        if gribfn is None:
            if utcdt < utcnow:
                LOG.info("MISSING %s", utcdt)
            continue
        with pygrib.open(gribfn) as grbs:
            grb = grbs[1]
            val: np.ndarray = grb["values"]
        os.unlink(gribfn)

        # Anything less than zero, we set to zero
        val = np.where(val < 0, 0, val)
        if total is None:
            total = val
        else:
            total += val

    if total is None:
        LOG.warning("nodata for %s, using zeros", dt)
        ncprecip[offset] = 0
        return
    # To save some space, we store a tigher CONUS domain
    # total.shape is 3500 x 7000, our 2700 x 6100
    # The upper left corner grib is -129.995, 54.995
    # The upper left corner netcdf is -125.995, 49.995
    # CAREFUL HERE!  The MRMS grid is North to South
    if total.shape != (3500, 7000):
        LOG.warning("total shape is %s, skipping", total.shape)
        return
    x0 = 400
    x1 = 400 + 6100
    y0 = 500
    y1 = 500 + 2700
    LOG.info("Writing precip at offset: %s [for_dep:%s]", offset, for_dep)
    ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])


@click.command()
@click.option(
    "--date",
    "dt",
    type=click.DateTime(),
    help="Date to process",
    required=True,
)
@click.option("--for-dep", is_flag=True, help="For Daily Erosion Project")
def main(dt: datetime, for_dep):
    """go main go"""
    if for_dep and (f"{dt:%m%d}" < "0411" or f"{dt:%m%d}" > "0615"):
        LOG.info("DEP not needed for %s", dt)
        return
    ncfn = get_daily_mrms_ncname(dt.year)
    if for_dep:
        ncfn = ncfn.replace("daily", "dep")
    with ncopen(ncfn, "a", timeout=300) as nc:
        run(nc, dt.date(), for_dep)


if __name__ == "__main__":
    main()
