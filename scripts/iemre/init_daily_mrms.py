'''
 Generate the storage netcdf file for 0.01deg MRMS data over the Midwest
'''
from pyiem import iemre
import netCDF4
import datetime
import numpy as np
import sys


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "/mesonet/data/iemre/%s_mw_mrms_daily.nc" % (ts.year, )
    nc = netCDF4.Dataset(fp, 'w')
    nc.title = "MRMS Daily Precipitation %s" % (ts.year,)
    nc.platform = "Grided Estimates"
    nc.description = "Midwest MRMS 0.01 degree grid"
    nc.institution = "Iowa State University, Ames, IA, USA"
    nc.source = "Iowa Environmental Mesonet"
    nc.project_id = "IEM"
    nc.realization = 1
    nc.Conventions = 'CF-1.0'
    nc.contact = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history = "%s Generated" % (
                            datetime.datetime.now().strftime("%d %B %Y"),)
    nc.comment = "No Comment at this time"

    # Setup Dimensions
    nc.createDimension('lat', (iemre.NORTH - iemre.SOUTH) * 100.0)
    nc.createDimension('lon', (iemre.EAST - iemre.WEST) * 100.0)
    days = ((ts.replace(year=ts.year+1)) - ts).days
    nc.createDimension('time', int(days))
    nc.createDimension('nv', 2)

    # Setup Coordinate Variables
    lat = nc.createVariable('lat', np.float, ('lat',))
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.bounds = "lat_bnds"
    lat.axis = "Y"
    # Grid centers
    lat[:] = np.arange(iemre.SOUTH + 0.005, iemre.NORTH, 0.01)

    lat_bnds = nc.createVariable('lat_bnds', np.float, ('lat', 'nv'))
    lat_bnds[:, 0] = np.arange(iemre.SOUTH, iemre.NORTH, 0.01)
    lat_bnds[:, 1] = np.arange(iemre.SOUTH + 0.01, iemre.NORTH + 0.01, 0.01)

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = np.arange(iemre.WEST, iemre.EAST, 0.01)

    lon_bnds = nc.createVariable('lon_bnds', np.float, ('lon', 'nv'))
    lon_bnds[:, 0] = np.arange(iemre.WEST, iemre.EAST, 0.01)
    lon_bnds[:, 1] = np.arange(iemre.WEST + 0.01, iemre.EAST + 0.01, 0.01)

    tm = nc.createVariable('time', np.float, ('time',))
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = np.arange(0, int(days))

    p01d = nc.createVariable('p01d', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    p01d.units = 'mm'
    p01d.long_name = 'Precipitation'
    p01d.standard_name = 'Precipitation'
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()

init_year(datetime.datetime(int(sys.argv[1]), 1, 1))
