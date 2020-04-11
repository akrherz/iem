"""Convert the CFS grib data into something mimicing IEMRE.

This will allow for downstream usage by PSIMS. Run from RUN_NOON.sh
"""
import os
import sys
import datetime

import numpy as np
from scipy.interpolate import NearestNDInterpolator
from tqdm import tqdm
import pygrib
from pyiem.util import utc, ncopen
from pyiem import iemre

DEFAULTS = {"srad": 0.0, "high_tmpk": 100.0, "low_tmpk": 400.0, "p01d": 0.0}
AGGFUNC = {
    "srad": np.add,
    "high_tmpk": np.maximum,
    "low_tmpk": np.minimum,
    "p01d": np.add,
}


def merge(nc, valid, gribname, vname):
    """Merge in the grib data"""
    fn = valid.strftime(
        (
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/cfs/%H/"
            + gribname
            + ".01.%Y%m%d%H.daily.grib2"
        )
    )
    if not os.path.isfile(fn):
        print("cfs2iemre missing %s, abort" % (fn,))
        sys.exit()
    grbs = pygrib.open(fn)
    lats = None
    lons = None
    xi, yi = np.meshgrid(iemre.XAXIS, iemre.YAXIS)
    for grib in tqdm(
        grbs, total=grbs.messages, desc=vname, disable=not sys.stdout.isatty()
    ):
        ftime = valid + datetime.timedelta(hours=grib.forecastTime)
        # move us safely back to get into the proper date
        cst = ftime - datetime.timedelta(hours=7)
        if cst.year != valid.year:
            continue
        if lats is None:
            lats, lons = grib.latlons()
        vals = grib.values
        nn = NearestNDInterpolator((lons.flat, lats.flat), vals.flat)
        vals = nn(xi, yi)
        tstep = iemre.daily_offset(cst.date())
        current = nc.variables[vname][tstep, :, :]
        if current.mask.all():
            current[:, :] = DEFAULTS[vname]
        nc.variables[vname][tstep, :, :] = AGGFUNC[vname](current, vals)

    if vname != "srad":
        return
    # HACK so above, we added all the solar radiation data together, so we
    # should divide this number by four to rectify it back to avg W m-2
    for tstep in range(nc.variables[vname].shape[0]):
        nc.variables[vname][tstep] = nc.variables[vname][tstep] / 4.0


def create_netcdf(valid):
    """Create and return the netcdf file"""
    ncfn = "/mesonet/data/iemre/cfs_%s.nc" % (valid.strftime("%Y%m%d%H"),)
    nc = ncopen(ncfn, "w")
    nc.title = "IEM Regridded CFS Member 1 Forecast %s" % (valid.year,)
    nc.platform = "Grided Forecast"
    nc.description = "IEM Regridded CFS on 0.125 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = "CF-1.0"
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = ("%s Generated") % (
        datetime.datetime.now().strftime("%d %B %Y"),
    )
    nc.comment = "No comment at this time"

    # Setup Dimensions
    nc.createDimension("lat", iemre.NY)
    nc.createDimension("lon", iemre.NX)
    days = iemre.daily_offset(valid.replace(month=12, day=31)) + 1
    nc.createDimension("time", int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable("lat", np.float, ("lat",))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = iemre.YAXIS

    lon = nc.createVariable("lon", np.float, ("lon",))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = iemre.XAXIS

    tm = nc.createVariable("time", np.float, ("time",))
    tm.units = "Days since %s-01-01 00:00:0.0" % (valid.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    high = nc.createVariable(
        "high_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    high.units = "K"
    high.scale_factor = 0.01
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable(
        "low_tmpk", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    low.units = "K"
    low.scale_factor = 0.01
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable(
        "p01d", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    p01d.units = "mm"
    p01d.scale_factor = 0.01
    p01d.long_name = "Precipitation"
    p01d.standard_name = "Precipitation"
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    rsds = nc.createVariable(
        "srad", np.uint16, ("time", "lat", "lon"), fill_value=65535
    )
    rsds.units = "W m-2"
    rsds.scale_factor = 0.01
    rsds.long_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.standard_name = "surface_downwelling_shortwave_flux_in_air"
    rsds.coordinates = "lon lat"
    rsds.description = "Global Shortwave Irradiance"

    nc.close()
    nc = ncopen(ncfn, "a")
    return nc


def main():
    """Go Main Go"""
    # Run for 12z yesterday
    today = datetime.date.today() - datetime.timedelta(days=1)
    for hour in [0, 6, 12, 18]:
        valid = utc(today.year, today.month, today.day, hour)
        # Create netcdf file
        nc = create_netcdf(valid)
        # merge in the data
        for gribname, vname in zip(
            ["dswsfc", "tmax", "tmin", "prate"],
            ["srad", "high_tmpk", "low_tmpk", "p01d"],
        ):
            merge(nc, valid, gribname, vname)
        # profit
        nc.close()


if __name__ == "__main__":
    main()
