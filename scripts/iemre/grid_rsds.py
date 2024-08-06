"""Do the gridding of Solar Radiation Data

This used to use MERRAv2 for non-realtime data, but a crude assessment found
ERA5land to produce better results.

Called from:
 - RUN_MIDNIGHT.sh for previous day
 - RUN_0Z.sh for 8 days ago
 - RUN_10_AFTER.sh at 11 PM for the current day
"""

# pylint: disable=unpacking-non-sequence
import datetime
import subprocess
from zoneinfo import ZoneInfo

import click
import numpy as np
import pygrib
import pyproj
import xarray as xr
from affine import Affine
from pyiem import iemre
from pyiem.util import archive_fetch, logger, ncopen, utc

LOG = logger()
P4326 = pyproj.Proj("EPSG:4326")
SWITCH_DATE = utc(2014, 10, 10, 20)


def try_era5land(ts: datetime.datetime, domain: str, dom: dict) -> bool:
    """Attempt to use ERA5Land data."""
    dd = "" if domain == "" else f"_{domain}"
    # inbound `ts` represents noon local time, we want values from 1 AM
    # till midnight
    one_am = ts.replace(hour=1).astimezone(ZoneInfo("UTC"))
    midnight = (
        (ts + datetime.timedelta(days=1))
        .replace(hour=0)
        .astimezone(ZoneInfo("UTC"))
    )
    # If years are equal, we don't have to span files
    idx0 = iemre.hourly_offset(one_am)
    idx1 = iemre.hourly_offset(midnight) + 1
    ncfn = f"/mesonet/data/era5{dd}/{one_am.year}_era5land_hourly.nc"
    if one_am.year == midnight.year:
        with ncopen(ncfn) as nc:
            total = np.ma.sum(nc.variables["rsds"][idx0:idx1, :, :], axis=0)
    else:
        with ncopen(ncfn) as nc:
            total = np.ma.sum(nc.variables["rsds"][idx0:, :, :], axis=0)
        ncfn = f"/mesonet/data/era5{dd}/{midnight.year}_era5land_hourly.nc"
        with ncopen(ncfn) as nc:
            total += np.ma.sum(nc.variables["rsds"][:idx1, :, :], axis=0)

    # If total is all missing, then we have no data
    if total.mask.all():
        return False
    # We wanna store as W m-2, so we just average out the data by hour
    total = total / 24.0

    aff = Affine(0.1, 0, dom["west"], 0, -0.1, dom["north"])
    vals = iemre.reproject2iemre(
        np.flipud(total), aff, P4326.crs, domain=domain
    )
    # 4 was found to be not enough to appease DEP's needs
    for shift in (-7, 7):
        for axis in (0, 1):
            vals_shifted = np.roll(vals, shift=shift, axis=axis)
            idx = ~vals_shifted.mask * vals.mask
            vals[idx] = vals_shifted[idx]

    avgval = np.ma.mean(vals)
    if avgval < 50:
        LOG.info("ERA5Land average value is %.2f, skipping", avgval)
        return False

    if domain != "":
        ncfn = iemre.get_daily_ncname(ts.year, domain)
        idx = iemre.daily_offset(ts.date())
        with ncopen(ncfn, "a") as nc:
            nc.variables["rsds"][idx, :, :] = vals
        return True
    # Jitter the grid to fill out edges along the coasts
    ds = xr.Dataset(
        {
            "rsds": xr.DataArray(
                vals,
                dims=("y", "x"),
            )
        }
    )
    iemre.set_grids(ts.date(), ds)
    subprocess.call(
        ["python", "db_to_netcdf.py", f"{ts:%Y}", f"{ts:%m}", f"{ts:%d}"]
    )

    return True


def do_gfs(ts: datetime.datetime, domain: str, dom: dict):
    """Attempt to use the GFS."""
    # Major complications with GFS 6 hour data being averaged and which
    # time period to use to get a "daily" value.
    # For europe, use 6z through 0z(tomorrow)
    # For china, use 0z through 18z
    dd = "" if domain == "" else f"_{domain}"

    # Rectify now back to hour modulo 6
    utcnow = ts.astimezone(ZoneInfo("UTC"))
    utcnow = utcnow.replace(
        hour=(utcnow.hour // 6) * 6, minute=0, second=0, microsecond=0
    ) - datetime.timedelta(hours=12)
    attempt = 4
    while attempt > 0:
        ppath = (
            f"{utcnow:%Y/%m/%d}/model/gfs/gfs_{utcnow:%Y%m%d%H}_iemre{dd}.nc"
        )
        with archive_fetch(ppath) as fn:
            if fn is None:
                attempt -= 1
                utcnow -= datetime.timedelta(hours=6)
                continue
            tidx = (ts.date() - utcnow.date()).days
            LOG.info("Using GFS %s for day index:%s", utcnow, tidx)
            with ncopen(fn) as nc:
                srad = nc.variables["srad"][tidx]
        ncfn = iemre.get_daily_ncname(ts.year, domain)
        idx = iemre.daily_offset(ts.date())
        with ncopen(ncfn, "a") as nc:
            # convert MJ/d to W/m^2
            nc.variables["rsds"][idx, :, :] = srad * 1e6 / 86400.0
        attempt = 0


def do_hrrr(ts: datetime.datetime):
    """Convert the hourly HRRR data to IEMRE grid"""
    LCC = pyproj.Proj(
        "+lon_0=-97.5 +y_0=0.0 +R=6367470. +proj=lcc +x_0=0.0 "
        "+units=m +lat_2=38.5 +lat_1=38.5 +lat_0=38.5"
    )
    total = None
    # So IEMRE is storing data from coast to coast, so we should be
    # aggressive about running for an entire calendar date
    for hr in range(24):
        utcnow = ts.replace(hour=hr).astimezone(ZoneInfo("UTC"))
        LOG.info("Considering timestamp %s", utcnow)
        # Try the newer f01 files, which have better data!
        ppath = (utcnow - datetime.timedelta(hours=1)).strftime(
            "%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf01.grib2"
        )
        with archive_fetch(ppath) as fn:
            if fn is not None:
                try:
                    grbs = pygrib.open(fn)
                    selgrbs = grbs.select(
                        name="Mean surface downward short-wave radiation flux"
                    )
                except Exception:
                    LOG.warning("Read of %s failed", fn)
                    continue
                # sometimes we have multiple grids :/
                if len(selgrbs) >= 4:
                    LOG.info("Using %s", fn)
                    # Goodie
                    subtotal = None
                    for g in selgrbs:
                        if total is None:
                            lat1 = g["latitudeOfFirstGridPointInDegrees"]
                            lon1 = g["longitudeOfFirstGridPointInDegrees"]
                            llcrnrx, llcrnry = LCC(lon1, lat1)
                            dx = g["DxInMetres"]
                            dy = g["DyInMetres"]
                        if subtotal is None:
                            subtotal = g.values
                        else:
                            subtotal += g.values
                    if total is None:
                        total = subtotal / float(len(selgrbs))
                    else:
                        total += subtotal / float(len(selgrbs))
                    continue

        ppath = utcnow.strftime(
            "%Y/%m/%d/model/hrrr/%H/hrrr.t%Hz.3kmf00.grib2"
        )
        with archive_fetch(ppath) as fn:
            if fn is None:
                continue
            grbs = pygrib.open(fn)
            try:
                if utcnow >= SWITCH_DATE:
                    grb = grbs.select(
                        name="Downward short-wave radiation flux"
                    )
                else:
                    grb = grbs.select(parameterNumber=192)
            except ValueError:
                # don't complain about late evening no-solar
                if utcnow.hour > 10 and utcnow.hour < 24:
                    LOG.info(" %s had no solar rad", fn)
                continue
            if not grb:
                LOG.info("Could not find SWDOWN in HRR %s", fn)
                continue
            LOG.info("Using %s", fn)
            g = grb[0]
            if total is None:
                total = g.values
                lat1 = g["latitudeOfFirstGridPointInDegrees"]
                lon1 = g["longitudeOfFirstGridPointInDegrees"]
                llcrnrx, llcrnry = LCC(lon1, lat1)
                dx = g["DxInMetres"]
                dy = g["DyInMetres"]
            else:
                total += g.values

    if total is None:
        LOG.info("found no HRRR data for %s", ts.strftime("%d %b %Y"))
        return

    # We wanna store as W m-2, so we just average out the data by hour
    total = total / 24.0
    affine_in = Affine(dx, 0.0, llcrnrx, 0.0, dy, llcrnry)

    ds = xr.Dataset(
        {
            "rsds": xr.DataArray(
                iemre.reproject2iemre(total, affine_in, LCC.crs),
                dims=("y", "x"),
            )
        }
    )
    iemre.set_grids(ts.date(), ds)
    subprocess.call(["python", "db_to_netcdf.py", f"--date={ts:%Y-%m-%d}"])


@click.command()
@click.option("--date", "dt", required=False, type=click.DateTime())
@click.option("--year", required=False, type=int, help="Run for Year,month")
@click.option("--month", required=False, type=int, help="Run for Year,month")
def main(dt, year, month):
    """Go Main Go"""
    queue = []
    if year is not None and month is not None:
        now = datetime.datetime(year, month, 1, 12)
        while now.month == month:
            queue.append(now)
            now += datetime.timedelta(days=1)
    else:
        queue.append(dt.replace(hour=12))
    for sts in queue:
        for domain, dom in iemre.DOMAINS.items():
            sts = sts.replace(tzinfo=dom["tzinfo"])
            if not try_era5land(sts, domain, dom):
                LOG.info("try_era5land failed to find data")
                if domain == "":
                    LOG.info("trying hrrr")
                    do_hrrr(sts)
                else:
                    LOG.info("trying GFS for domain %s", domain)
                    do_gfs(sts, domain, dom)


if __name__ == "__main__":
    main()
