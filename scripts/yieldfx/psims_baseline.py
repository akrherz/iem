"""Generate PSIMs Tiles for baseline.

Run from RUN_2AM.sh for yesterday and eight days ago, so to pick up POWER.
"""

import os
import sys
from datetime import date, datetime, timedelta

import click
import numpy as np
from metpy.units import units
from pyiem.grid.nav import IEMRE
from pyiem.iemre import get_daily_ncname
from pyiem.meteorology import gdd
from pyiem.util import convert_value, logger, ncopen
from tqdm import tqdm

LOG = logger()


def make_netcdf(ncfn, valid, west, south):
    """Make our netcdf"""
    totaldays = (
        valid.replace(month=12, day=31)
        - valid.replace(year=1980, month=1, day=1)
    ).days + 1
    with ncopen(ncfn, "w") as nc:
        # Dimensions
        nc.createDimension("time", totaldays)
        nc.createDimension("lat", 16)  # 0.125 grid over 2 degrees
        nc.createDimension("lon", 16)
        # Coordinate Dimensions
        time = nc.createVariable("time", int, ("time",))
        time.units = "days since 1980-01-01 00:00:00"
        time[:] = np.arange(0, totaldays)

        lat = nc.createVariable("lat", float, ("lat"))
        lat.units = "degrees_north"
        lat.long_name = "latitude"
        lat[:] = np.arange(south + 0.125 / 2.0, south + 2.0, 0.125)

        lon = nc.createVariable("lon", float, ("lon"))
        lon.units = "degrees_east"
        lon.long_name = "longitude"
        lon[:] = np.arange(west + 0.125 / 2.0, west + 2.0, 0.125)

        prcp = nc.createVariable(
            "prcp", float, ("time", "lat", "lon"), fill_value=1e20
        )
        prcp.units = "mm/day"
        prcp.long_name = "daily total precipitation"

        tmax = nc.createVariable(
            "tmax", float, ("time", "lat", "lon"), fill_value=1e20
        )
        tmax.units = "degrees C"
        tmax.long_name = "daily maximum temperature"

        tmin = nc.createVariable(
            "tmin", float, ("time", "lat", "lon"), fill_value=1e20
        )
        tmin.units = "degrees C"
        tmin.long_name = "daily minimum temperature"

        gddf = nc.createVariable(
            "gdd_f", float, ("time", "lat", "lon"), fill_value=1e20
        )
        gddf.units = "degrees F"
        gddf.long_name = "Growing Degree Days F (base 50 ceiling 86)"

        srad = nc.createVariable(
            "srad", float, ("time", "lat", "lon"), fill_value=1e20
        )
        srad.units = "MJ"
        srad.long_name = "daylight average incident shortwave radiation"


def copy_iemre(nc, ncdate0: date, ncdate1: date, islice, jslice):
    """Copy IEMRE data from a given year to **inclusive** dates."""
    rencfn = get_daily_ncname(ncdate0.year)
    if not os.path.isfile(rencfn):
        LOG.info("reanalysis fn %s missing", rencfn)
        return
    with ncopen(rencfn) as renc:
        # Compute offsets for yieldfx file
        tidx0 = (ncdate0 - date(1980, 1, 1)).days
        tidx1 = (ncdate1 - date(1980, 1, 1)).days
        yfx_slice = slice(tidx0, tidx1 + 1)
        # Compute offsets for the reanalysis file
        tidx0 = (ncdate0 - date(ncdate0.year, 1, 1)).days
        tidx1 = (ncdate1 - date(ncdate0.year, 1, 1)).days
        re_slice = slice(tidx0, tidx1 + 1)

        highc = convert_value(
            renc.variables["high_tmpk"][re_slice, jslice, islice],
            "degK",
            "degC",
        )
        lowc = convert_value(
            renc.variables["low_tmpk"][re_slice, jslice, islice],
            "degK",
            "degC",
        )
        nc.variables["tmax"][yfx_slice, :, :] = highc
        nc.variables["tmin"][yfx_slice, :, :] = lowc
        nc.variables["gdd_f"][yfx_slice, :, :] = gdd(
            units("degC") * highc, units("degC") * lowc
        )
        nc.variables["prcp"][yfx_slice, :, :] = renc.variables["p01d"][
            re_slice, jslice, islice
        ]
        # Special care needed for solar radiation filling
        for rt, nt in zip(
            list(range(re_slice.start, re_slice.stop)),
            list(range(yfx_slice.start, yfx_slice.stop)),
            strict=False,
        ):
            # IEMRE power_swdn is MJ, test to see if data exists
            srad = renc.variables["power_swdn"][rt, jslice, islice]
            if srad.mask.any():
                # IEMRE rsds uses W m-2, we want MJ
                srad = (
                    renc.variables["rsds"][rt, jslice, islice]
                    * 86400.0
                    / 1000000.0
                )
            nc.variables["srad"][nt, :, :] = srad


def tile_extraction(nc, valid, west, south, fullmode):
    """Do our tile extraction"""
    # update model metadata
    i, j = IEMRE.find_ij(west, south)
    islice = slice(i, i + 16)
    jslice = slice(j, j + 16)
    if fullmode:
        for year in range(1980, valid.year + 1):
            copy_iemre(
                nc,
                date(year, 1, 1),
                date(year, 12, 31),
                islice,
                jslice,
            )
    else:
        copy_iemre(nc, valid, valid, islice, jslice)


def qc(nc):
    """Quick QC of the file."""
    for i, time in enumerate(nc.variables["time"][:]):
        ts = date(1980, 1, 1) + timedelta(days=int(time))
        avgv = np.mean(nc.variables["srad"][i, :, :])
        if avgv > 0:
            continue
        print(f"ts: {ts} avgv: {avgv}")
    print("done...")


def workflow(valid, ncfn, west, south, fullmode):
    """Make the magic happen"""
    basedir = "/mesonet/share/pickup/yieldfx/baseline"
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    fullpath = f"{basedir}/{ncfn}"
    if fullmode:
        make_netcdf(fullpath, valid, west, south)
    with ncopen(fullpath, "a") as nc:
        tile_extraction(nc, valid, west, south, fullmode)
        if fullmode:
            qc(nc)


@click.command()
@click.option("--date", "dt", type=click.DateTime(), help="Date to process")
@click.option("--full", is_flag=True, help="Full replacement mode")
def main(dt: datetime, full):
    """Go Main Go"""
    if dt is not None:
        dt = dt.date()
    # Create tiles to cover 12 states
    progress = tqdm(np.arange(-104, -80, 2), disable=not sys.stdout.isatty())
    for west in progress:
        progress.set_description(f"{west:.2f}")
        for south in np.arange(36, 50, 2):
            # psims divides its data up into 2x2-degree tiles,
            # with the first number in the file name being number
            # of tiles since 90 degrees north, and the second number
            # being number of tiles since -180 degrees eas
            yt = (90 - south) / 2
            xt = (180 - (0 - west)) / 2 + 1
            ncfn = f"clim_{yt:04.0f}_{xt:04.0f}.tile.nc4"
            workflow(dt, ncfn, west, south, full)


if __name__ == "__main__":
    main()
