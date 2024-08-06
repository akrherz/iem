"""Merge the 0.01x0.01 Q3 24 hour precip data estimates.

called from RUN_10_AFTER.sh
"""

import datetime
import gzip
import os
import tempfile
from zoneinfo import ZoneInfo

import click
import numpy as np
import pygrib
from pyiem import iemre, mrms
from pyiem.util import logger, ncopen, utc

LOG = logger()
TMP = "/mesonet/tmp"

# MultiSensor_QPE_01H_Pass2 after, GaugeCorr_QPE_01H before
PRODFLIP = utc(2020, 10, 13, 19)


def run(dt: datetime.date, for_dep: bool):
    """Update netcdf file with the MRMS data

    Args:
      dt (datetime.date): date to process
      for_dep (bool): for Daily Erosion Project
    """
    ncfn = iemre.get_daily_mrms_ncname(dt.year)
    if for_dep:
        ncfn = ncfn.replace("daily", "dep")
    nc = ncopen(ncfn, "a", timeout=300)
    offset = iemre.daily_offset(dt)
    if for_dep:
        offset = offset - iemre.daily_offset(datetime.date(dt.year, 4, 11))
    ncprecip = nc.variables["p01d"]

    midnight = datetime.datetime(
        dt.year, dt.month, dt.day, tzinfo=ZoneInfo("America/Chicago")
    )
    utcnow = utc()
    total = None
    lats = None
    UTC = ZoneInfo("UTC")
    # Stop at 6 PM if we are using DEP
    for hr in range(1, 18 if for_dep else 25):
        utcdt = (midnight + datetime.timedelta(hours=hr)).astimezone(UTC)
        if utcdt > utcnow:
            continue
        gribfn = None
        qcprod = "MultiSensor_QPE_01H_Pass2"
        if utcdt < PRODFLIP:
            qcprod = "GaugeCorr_QPE_01H"
        for prefix in [qcprod, "RadarOnly_QPE_01H"]:
            fn = mrms.fetch(prefix, utcdt)
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
        grbs = pygrib.open(gribfn)
        grb = grbs[1]
        if lats is None:
            lats, _ = grb.latlons()
        os.unlink(gribfn)

        val = grb["values"]
        # Anything less than zero, we set to zero
        val = np.where(val < 0, 0, val)
        if total is None:
            total = val
        else:
            total += val

    if lats is None:
        LOG.warning("nodata for %s, using zeros", dt)
        ncprecip[offset, :, :] = 0
        nc.close()
        return
    # CAREFUL HERE!  The MRMS grid is North to South
    # set top (smallest y)
    dom = iemre.DOMAINS[""]
    y0 = int((lats[0, 0] - dom["north"]) * 100.0)
    y1 = int((lats[0, 0] - dom["south"]) * 100.0)
    x0 = int((dom["west"] - mrms.WEST) * 100.0)
    x1 = int((dom["east"] - mrms.WEST) * 100.0)
    LOG.info("Writing precip at offset: %s [for_dep:%s]", offset, for_dep)
    ncprecip[offset, :, :] = np.flipud(total[y0:y1, x0:x1])
    nc.close()


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to process")
@click.option("--for-dep", is_flag=True, help="For Daily Erosion Project")
def main(dt, for_dep):
    """go main go"""
    if for_dep and (f"{dt:%m%d}" < "0411" or f"{dt:%m%d}" > "0615"):
        LOG.info("DEP not needed for %s", dt)
        return
    run(dt.date(), for_dep)


if __name__ == "__main__":
    main()
