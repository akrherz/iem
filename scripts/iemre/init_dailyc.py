"""Generate the IEMRE climatology file, hmmm"""
from __future__ import print_function
import datetime

import netCDF4
import numpy as np
from pyiem import iemre

BASEDIR = "/mesonet/data/iemre"


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "%s/mw_dailyc.nc" % (BASEDIR, )
    nc = netCDF4.Dataset(fp, 'w')
    nc.title = "IEM Daily Reanalysis Climatology %s" % (ts.year,)
    nc.platform = "Grided Climatology"
    nc.description = "IEM daily analysis on a 0.25 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = 'CF-1.0'  # *cough*
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
                    datetime.datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension('lat', iemre.NY)
    nc.createDimension('lon', iemre.NX)
    ts2 = datetime.datetime(ts.year + 1, 1, 1)
    days = (ts2 - ts).days
    nc.createDimension('time', int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable('lat', np.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = iemre.YAXIS

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = iemre.XAXIS

    tm = nc.createVariable('time', np.float, ('time',))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    # Tracked variables
    high = nc.createVariable('high_tmpk', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    high.units = "K"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable('low_tmpk', np.float, ('time', 'lat', 'lon'),
                            fill_value=1.e20)
    low.units = "K"
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable('p01d', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    p01d.units = 'mm'
    p01d.long_name = 'Precipitation'
    p01d.standard_name = 'Precipitation'
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()


def main():
    """Go Main"""
    init_year(datetime.datetime(2000, 1, 1))


if __name__ == '__main__':
    main()
