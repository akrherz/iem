"""Generate PSIMs Tiles.

Run from RUN_NOON.sh for the previous UTC date."""

import os
from datetime import date, timedelta

import numpy as np
from metpy.units import units
from pyiem.grid.nav import IEMRE
from pyiem.iemre import daily_offset, get_daily_ncname
from pyiem.meteorology import gdd
from pyiem.util import convert_value, ncopen


def make_netcdf(fullpath, valid, west, south):
    """Make our netcdf"""
    nc = ncopen(fullpath, "w")
    # Dimensions
    totaldays = (
        valid.replace(month=12, day=31) - valid.replace(month=1, day=1)
    ).days + 1
    nc.createDimension("time", totaldays)
    nc.createDimension("lat", 16)  # 0.125 grid over 2 degrees
    nc.createDimension("lon", 16)
    # Coordinate Dimensions
    time = nc.createVariable("time", int, ("time",))
    time.units = "days since %s-01-01 00:00:00" % (valid.year,)
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

    # did not do vp or cropland
    nc.close()
    nc = ncopen(fullpath, "a")
    return nc


def replace_cfs(nc, valid, islice, jslice):
    """Copy CFS data into the given year."""
    tidx0 = (valid - date(valid.year, 1, 1)).days
    tidx1 = (date(valid.year, 12, 31) - date(valid.year, 1, 1)).days
    cfsnc = ncopen(valid.strftime("/mesonet/data/iemre/cfs_%Y%m%d%H.nc"))
    tidx = daily_offset(valid + timedelta(days=1))
    tslice = slice(tidx0 + 1, tidx1 + 1)
    # CFS is W m-2, we want MJ
    nc.variables["srad"][tslice, :, :] = (
        cfsnc.variables["srad"][tidx:, jslice, islice] * 86400.0 / 1000000.0
    )
    highc = convert_value(
        cfsnc.variables["high_tmpk"][tidx:, jslice, islice], "degK", "degC"
    )
    lowc = convert_value(
        cfsnc.variables["low_tmpk"][tidx:, jslice, islice], "degK", "degC"
    )
    nc.variables["tmax"][tslice, :, :] = highc
    nc.variables["tmin"][tslice, :, :] = lowc
    nc.variables["gdd_f"][tslice, :, :] = gdd(
        units("degC") * highc, units("degC") * lowc
    )
    nc.variables["prcp"][tslice, :, :] = cfsnc.variables["p01d"][
        tidx:, jslice, islice
    ]
    cfsnc.close()


def copy_iemre(nc, fromyear, ncdate0, ncdate1, islice, jslice):
    """Copy IEMRE data from a given year to **inclusive** dates."""
    rencfn = get_daily_ncname(fromyear)
    if not os.path.isfile(rencfn):
        print("reanalysis fn %s missing" % (rencfn,))
        return
    renc = ncopen(rencfn)
    tidx0 = (ncdate0 - date(fromyear, 1, 1)).days
    tidx1 = (ncdate1 - date(fromyear, 1, 1)).days
    tslice = slice(tidx0, tidx1 + 1)
    # time steps to fill
    tsteps = (tidx1 - tidx0) + 1
    # figure out the slice
    if ncdate0.strftime("%m%d") == "0101":
        retslice = slice(0, tsteps)
    else:
        retslice = slice(0 - tsteps, None)
    highc = convert_value(
        renc.variables["high_tmpk"][retslice, jslice, islice], "degK", "degC"
    )
    lowc = convert_value(
        renc.variables["low_tmpk"][retslice, jslice, islice], "degK", "degC"
    )
    nc.variables["tmax"][tslice, :, :] = highc
    nc.variables["tmin"][tslice, :, :] = lowc
    nc.variables["gdd_f"][tslice, :, :] = gdd(
        units("degC") * highc, units("degC") * lowc
    )
    nc.variables["prcp"][tslice, :, :] = renc.variables["p01d"][
        retslice, jslice, islice
    ]
    for rt, nt in zip(
        list(
            range(
                retslice.start, 0 if retslice.stop is None else retslice.stop
            )
        ),
        list(range(tslice.start, tslice.stop)),
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
    renc.close()


def tile_extraction(nc, valid, west, south):
    """Do our tile extraction"""
    # update model metadata
    i, j = IEMRE.find_ij(west, south)
    islice = slice(i, i + 16)
    jslice = slice(j, j + 16)
    # Current year IEMRE should be substituted for this year's data
    copy_iemre(nc, valid.year, date(valid.year, 1, 1), valid, islice, jslice)
    replace_cfs(nc, valid, islice, jslice)


def qc(nc):
    """Quick QC of the file."""
    for i, time in enumerate(nc.variables["time"][:]):
        ts = date(2019, 1, 1) + timedelta(days=int(time))
        avgv = np.mean(nc.variables["srad"][i, :, :])
        if avgv > 0:
            continue
        print("ts: %s avgv: %s" % (ts, avgv))


def workflow(valid, ncfn, west, south):
    """Make the magic happen"""
    basedir = "/mesonet/share/pickup/yieldfx/%s" % (valid.year,)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    nc = make_netcdf("%s/%s" % (basedir, ncfn), valid, west, south)
    tile_extraction(nc, valid, west, south)
    nc.close()


def main():
    """Go Main Go"""
    today = date.today() - timedelta(days=2)
    # Create tiles to cover IA, IL, IN
    for west in np.arange(-104, -80, 2):
        for south in np.arange(36, 50, 2):
            # psims divides its data up into 2x2-degree tiles,
            # with the first number in the file name being number
            # of tiles since 90 degrees north, and the second number
            # being number of tiles since -180 degrees eas
            ncfn = "clim_%04i_%04i.tile.nc4" % (
                (90 - south) / 2,
                (180 - (0 - west)) / 2 + 1,
            )
            workflow(today, ncfn, west, south)


if __name__ == "__main__":
    main()
