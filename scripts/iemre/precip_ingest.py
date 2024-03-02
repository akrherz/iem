"""Ingest Stage IV Hourly Files.

1. Copies to hourly stage IV netCDF files
2. Copies hourly stage IV netCDF to hourly IEMRE
"""

import datetime
import os

import click
import numpy as np
import pygrib
from pyiem import iemre
from pyiem.util import logger, ncopen
from scipy.interpolate import NearestNDInterpolator

LOG = logger()


def get_p01m_status(valid):
    """Figure out what our current status is of this hour."""
    tidx = iemre.hourly_offset(valid)
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
    tidx = iemre.hourly_offset(valid)
    fn = valid.strftime(
        "/mesonet/ARCHIVE/data/%Y/%m/%d/stage4/ST4.%Y%m%d%H.01h.grib"
    )
    if not os.path.isfile(fn):
        LOG.info("stage4_ingest: missing file %s", fn)
        return
    gribs = pygrib.open(fn)
    grb = gribs[1]
    val = grb.values
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
    LOG.debug(
        "write p01m to stage4 netcdf min: %.2f avg: %.2f max: %.2f",
        np.min(val),
        np.mean(val),
        np.max(val),
    )
    return


def copy_to_iemre(valid):
    """verbatim copy over to IEMRE."""
    tidx = iemre.hourly_offset(valid)
    ncfn = f"/mesonet/data/stage4/{valid.year}_stage4_hourly.nc"
    with ncopen(ncfn, "a", timeout=300) as nc:
        lats = nc.variables["lat"][:]
        lons = nc.variables["lon"][:]
        val = nc.variables["p01m"][tidx]

    # Our data is 4km, iemre is 0.125deg, so we stride some to cut down on mem
    stride = slice(None, None, 3)
    lats = np.ravel(lats[stride, stride])
    lons = np.ravel(lons[stride, stride])
    vals = np.ravel(val[stride, stride])
    nn = NearestNDInterpolator((lons, lats), vals)
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    res = nn(xi, yi)

    # Lets clip bad data
    # 10 inches per hour is bad data
    res = np.where(np.logical_or(res < 0, res > 250), 0.0, res)

    # Open up our RE file
    with ncopen(iemre.get_hourly_ncname(valid.year), "a", timeout=300) as nc:
        nc.variables["p01m"][tidx, :, :] = res
    LOG.info(
        "wrote data to hourly IEMRE min: %.2f avg: %.2f max: %.2f",
        np.min(res),
        np.mean(res),
        np.max(res),
    )


def workflow(valid, force_copy):
    """Our stage IV workflow."""
    # Figure out what the current status is
    p01m_status = get_p01m_status(valid)
    if np.ma.is_masked(p01m_status) or p01m_status < 2 or force_copy:
        # merge in the raw hourly data
        ingest_hourly_grib(valid)

    copy_to_iemre(valid)


@click.command()
@click.option("--valid", "ts", type=click.DateTime(), help="Specific UTC")
@click.option("--valid12z", "ets", type=click.DateTime(), help="12z UTC")
def main(ts, ets):
    """Go Main"""
    if ts is not None:
        ts = ts.replace(tzinfo=datetime.timezone.utc)
        workflow(ts, True)
        return
    # Otherwise we are running for an explicit 12z to 12z period, copy only
    ets = ets.replace(tzinfo=datetime.timezone.utc)
    now = ets - datetime.timedelta(hours=23)
    while now <= ets:
        workflow(now, False)
        now += datetime.timedelta(hours=1)


if __name__ == "__main__":
    main()
