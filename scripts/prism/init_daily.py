"""Generate the yearly PRISM file to hold our data """
from pyiem import prism
import netCDF4
import datetime
import numpy as np
import sys


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fn = "/mesonet/data/prism/%s_daily.nc" % (ts.year, )
    nc = netCDF4.Dataset(fn, 'w')
    nc.title = "PRISM Daily Data for %s" % (ts.year,)
    nc.platform = "Grided Observations"
    nc.description = "PRISM Data on a 0.04 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = 'CF-1.0'
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = ("%s Generated"
                  ) % (datetime.datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension('lat', prism.NY)
    nc.createDimension('lon', prism.NX)
    days = ((ts.replace(year=ts.year+1)) - ts).days
    nc.createDimension('time', int(days))

    # Setup Coordinate Variables
    lat = nc.createVariable('lat', np.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = prism.YAXIS

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = prism.XAXIS

    tm = nc.createVariable('time', np.float, ('time',))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    # Tracked variables
    high = nc.createVariable('tmax', np.float, ('time', 'lat', 'lon'),
                             fill_value=-9999.)
    high.units = "C"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high.coordinates = "lon lat"

    low = nc.createVariable('tmin', np.float, ('time', 'lat', 'lon'),
                            fill_value=-9999.)
    low.units = "C"
    low.long_name = "2m Air Temperature Daily High"
    low.standard_name = "2m Air Temperature"
    low.coordinates = "lon lat"

    p01d = nc.createVariable('ppt', np.float, ('time', 'lat', 'lon'),
                             fill_value=-9999.)
    p01d.units = 'mm'
    p01d.long_name = 'Precipitation'
    p01d.standard_name = 'Precipitation'
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()

if __name__ == '__main__':
    init_year(datetime.datetime(int(sys.argv[1]), 1, 1))
