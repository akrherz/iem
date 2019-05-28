"""Generate PSIMs Tiles for baseline."""
import datetime
import os
import sys

import numpy as np
from pyiem import iemre
from pyiem.datatypes import temperature
from pyiem.util import ncopen
from pyiem.meteorology import gdd


def make_netcdf(fullpath, valid, west, south):
    """Make our netcdf"""
    nc = ncopen(fullpath, 'w')
    # Dimensions
    totaldays = (valid.replace(month=12, day=31) -
                 valid.replace(year=1980, month=1, day=1)).days + 1
    nc.createDimension('time', totaldays)
    nc.createDimension('lat', 16)  # 0.125 grid over 2 degrees
    nc.createDimension('lon', 16)
    # Coordinate Dimensions
    time = nc.createVariable('time', np.int, ('time', ))
    time.units = "days since 1980-01-01 00:00:00"
    time[:] = np.arange(0, totaldays)

    lat = nc.createVariable('lat', np.float, ('lat'))
    lat.units = 'degrees_north'
    lat.long_name = 'latitude'
    lat[:] = np.arange(south + 0.125/2., south + 2., 0.125)

    lon = nc.createVariable('lon', np.float, ('lon'))
    lon.units = 'degrees_east'
    lon.long_name = 'longitude'
    lon[:] = np.arange(west + 0.125/2., west + 2., 0.125)

    prcp = nc.createVariable('prcp', np.float, ('time', 'lat', 'lon'),
                             fill_value=1e20)
    prcp.units = "mm/day"
    prcp.long_name = "daily total precipitation"

    tmax = nc.createVariable('tmax', np.float, ('time', 'lat', 'lon'),
                             fill_value=1e20)
    tmax.units = "degrees C"
    tmax.long_name = "daily maximum temperature"

    tmin = nc.createVariable('tmin', np.float, ('time', 'lat', 'lon'),
                             fill_value=1e20)
    tmin.units = "degrees C"
    tmin.long_name = "daily minimum temperature"

    gddf = nc.createVariable(
        'gdd_f', np.float, ('time', 'lat', 'lon'), fill_value=1e20
    )
    gddf.units = "degrees F"
    gddf.long_name = "Growing Degree Days F (base 50 ceiling 86)"

    srad = nc.createVariable('srad', np.float, ('time', 'lat', 'lon'),
                             fill_value=1e20)
    srad.units = "MJ"
    srad.long_name = "daylight average incident shortwave radiation"

    # did not do vp or cropland
    nc.close()
    nc = ncopen(fullpath, 'a')
    return nc


def copy_iemre(nc, fromyear, ncdate0, ncdate1, islice, jslice):
    """Copy IEMRE data from a given year to **inclusive** dates."""
    rencfn = iemre.get_daily_ncname(fromyear)
    if not os.path.isfile(rencfn):
        print("reanalysis fn %s missing" % (rencfn, ))
        return
    renc = ncopen(rencfn)
    tidx0 = (ncdate0 - datetime.date(1980, 1, 1)).days
    tidx1 = (ncdate1 - datetime.date(1980, 1, 1)).days
    tslice = slice(tidx0, tidx1 + 1)
    # time steps to fill
    tsteps = (tidx1 - tidx0) + 1
    # figure out the slice
    if ncdate0.strftime("%m%d") == "0101":
        retslice = slice(0, tsteps)
    else:
        retslice = slice(0 - tsteps, None)
    # print("copy_iemre from %s filling %s steps nc: %s iemre: %s" % (
    #    fromyear, tsteps, tslice, retslice
    # ))
    highc = temperature(
        renc.variables['high_tmpk'][retslice, jslice, islice], 'K'
    ).value('C')
    lowc = temperature(
        renc.variables['low_tmpk'][retslice, jslice, islice], 'K'
    ).value('C')
    nc.variables['tmax'][tslice, :, :] = highc
    nc.variables['tmin'][tslice, :, :] = lowc
    nc.variables['gdd_f'][tslice, :, :] = gdd(
        temperature(highc, "C"),
        temperature(lowc, "C")
    )
    nc.variables['prcp'][tslice, :, :] = (
        renc.variables['p01d'][retslice, jslice, islice])
    for rt, nt in zip(
            list(range(
                retslice.start,
                0 if retslice.stop is None else retslice.stop)),
            list(range(tslice.start, tslice.stop)),):
        # IEMRE power_swdn is MJ, test to see if data exists
        srad = renc.variables['power_swdn'][rt, jslice, islice]
        if srad.mask.any():
            # IEMRE rsds uses W m-2, we want MJ
            srad = (
                renc.variables['rsds'][rt, jslice, islice] *
                86400. / 1000000.
            )
        nc.variables['srad'][nt, :, :] = srad
    renc.close()


def tile_extraction(nc, valid, west, south):
    """Do our tile extraction"""
    # update model metadata
    i, j = iemre.find_ij(west, south)
    islice = slice(i, i+16)
    jslice = slice(j, j+16)
    for year in range(1980, valid.year + 1):
        copy_iemre(
            nc, year, datetime.date(year, 1, 1), datetime.date(year, 12, 31),
            islice, jslice)


def qc(nc):
    """Quick QC of the file."""
    for i, time in enumerate(nc.variables['time'][:]):
        ts = datetime.date(1980, 1, 1) + datetime.timedelta(days=int(time))
        avgv = np.mean(nc.variables['srad'][i, :, :])
        if avgv > 0:
            continue
        print("ts: %s avgv: %s" % (ts, avgv))
    print("done...")


def workflow(valid, ncfn, west, south):
    """Make the magic happen"""
    basedir = "/mesonet/share/pickup/yieldfx/baseline"
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    nc = make_netcdf("%s/%s" % (basedir, ncfn), valid, west, south)
    tile_extraction(nc, valid, west, south)
    qc(nc)
    nc.close()


def main(argv):
    """Go Main Go"""
    valid = datetime.date(int(argv[1]), 12, 31)
    # Run for the 12z file **two days ago**, the issue is that for a year
    # without a leap day, previous year filling will ask for one too many
    # days that currently does not have data
    # Create tiles to cover IA, IL, IN
    for west in np.arange(-104, -80, 2):
        for south in np.arange(36, 50, 2):
            # psims divides its data up into 2x2-degree tiles,
            # with the first number in the file name being number
            # of tiles since 90 degrees north, and the second number
            # being number of tiles since -180 degrees eas
            ncfn = "clim_%04i_%04i.tile.nc4" % (
                (90 - south) / 2, (180 - (0 - west)) / 2 + 1
            )
            workflow(valid, ncfn, west, south)


if __name__ == '__main__':
    main(sys.argv)
