"""Ingest Stage IV Hourly Files.

1. Copies to hourly stage IV netCDF files
2. Copies hourly stage IV netCDF to hourly IEMRE
"""

import warnings
from datetime import datetime, timedelta, timezone

import click
import numpy as np
import pygrib
from pyiem.grid.nav import get_nav
from pyiem.iemre import get_hourly_ncname, hourly_offset, reproject2iemre
from pyiem.stage4 import ARCHIVE_FLIP
from pyiem.util import archive_fetch, logger, ncopen

# silence warning when we squeeze data into netcdf
warnings.simplefilter("ignore", RuntimeWarning)
LOG = logger()


def get_p01m_status(valid):
    """Figure out what our current status is of this hour."""
    tidx = hourly_offset(valid)
    with ncopen(
        f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc",
        timeout=300,
    ) as nc:
        # 2 prism_adjust_stage4 ran
        # 1 copied hourly data in
        # 0 nothing happened
        p01m_status = nc.variables["p01m_status"][tidx]
    LOG.info("p01m_status is %s for valid %s", p01m_status, valid)
    return p01m_status


def ingest_hourly_grib(valid):
    """Copy the hourly grib data into the netcdf storage.

    Returns:
      int value of the new p01m_status
    """
    tidx = hourly_offset(valid)
    ppath = valid.strftime("%Y/%m/%d/stage4/ST4.%Y%m%d%H.01h.grib")
    with archive_fetch(ppath) as fn:
        if fn is None:
            LOG.info("stage4_ingest: missing file %s", fn)
            return
        gribs = pygrib.open(fn)
        grb = gribs[1]
        val = grb.values
        gribs.close()
    # values over 10 inches are bad
    val = np.where(val > 250.0, 0, val)

    ncfn = f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc"
    with ncopen(ncfn, "a", timeout=300) as nc:
        p01m = nc.variables["p01m"]
        # account for legacy grid prior to 2002
        if val.shape == (880, 1160):
            p01m[tidx, 1:, :] = val[:, 39:]
        else:
            p01m[tidx, :, :] = val
        nc.variables["p01m_status"][tidx] = 1
    LOG.info(
        "write p01m to stage4 netcdf min: %.2f avg: %.2f max: %.2f",
        np.min(val),
        np.mean(val),
        np.max(val),
    )
    return


def copy_to_iemre(valid):
    """verbatim copy over to IEMRE."""
    tidx = hourly_offset(valid)
    ncfn = f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc"
    with ncopen(ncfn, "a", timeout=300) as nc:
        val = nc.variables["p01m"][tidx]
        LOG.info("stage4 mean: %.2f max: %.2f", np.mean(val), np.max(val))

    # Reproject to IEMRE
    aff = (
        get_nav("STAGE4").affine
        if valid >= ARCHIVE_FLIP
        else get_nav("STAGE4_PRE2002", "").affine
    )
    res = reproject2iemre(val, aff, get_nav("STAGE4").crs, domain="conus")
    LOG.info("iemre mean: %.2f max: %.2f", np.mean(res), np.max(res))

    # Lets clip bad data
    # 10 inches per hour is bad data
    res = np.ma.where(np.ma.logical_or(res < 0, res > 250), 0.0, res)
    LOG.info("iemre mean: %.2f max: %.2f", np.mean(res), np.max(res))

    # Open up our RE file
    with ncopen(
        get_hourly_ncname(valid.year, domain="conus"), "a", timeout=300
    ) as nc:
        nc.variables["p01m"][tidx] = res
    LOG.info(
        "wrote data to hourly IEMRE min: %.2f avg: %.2f max: %.2f",
        np.min(res),
        np.mean(res),
        np.max(res),
    )


def era5workflow(valid: datetime, domain: str):
    """Copy ERA5Land to IEMRE."""
    # NOTE, this may be off-by-one
    idx = hourly_offset(valid)
    dd = "" if domain == "" else f"_{domain}"
    with ncopen(f"/mesonet/data/era5{dd}/{valid:%Y}_era5land_hourly.nc") as nc:
        p01m = nc.variables["p01m"][idx]
    # Convert trace/drizzle to 0, values < 0.01in or .254mm
    p01m[p01m < 0.254] = 0
    affine_in = get_nav("ERA5LAND", domain).affine
    val = reproject2iemre(p01m, affine_in, "EPSG:4326", domain=domain)
    with ncopen(
        get_hourly_ncname(valid.year, domain=domain), "a", timeout=300
    ) as nc:
        nc.variables["p01m"][idx] = val


def workflow(valid: datetime, domain: str, force_copy: bool):
    """Our stage IV workflow."""
    if valid.year < 1997 or domain != "":
        era5workflow(valid, domain)
        return
    # Figure out what the current status is
    p01m_status = get_p01m_status(valid)
    if np.ma.is_masked(p01m_status) or p01m_status < 2 or force_copy:
        # merge in the raw hourly data
        ingest_hourly_grib(valid)

    copy_to_iemre(valid)


@click.command()
@click.option("--valid", "ts", type=click.DateTime(), help="Specific UTC")
@click.option("--valid12z", "ets", type=click.DateTime(), help="12z UTC")
@click.option("--domain", default="conus", help="IEMRE Domain")
def main(ts: datetime | None, ets: datetime | None, domain: str):
    """Go Main"""
    if ts is not None:
        ts = ts.replace(tzinfo=timezone.utc)
        workflow(ts, domain, True)
        return
    # Otherwise we are running for an explicit 12z to 12z period, copy only
    ets = ets.replace(tzinfo=timezone.utc)
    now = ets - timedelta(hours=23)
    while now <= ets:
        workflow(now, domain, False)
        now += timedelta(hours=1)


if __name__ == "__main__":
    main()
