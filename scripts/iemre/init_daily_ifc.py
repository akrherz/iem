"""
 Generate the storage netcdf file for Iowa Flood Center Precip
"""
import netCDF4
import datetime
import numpy as np
import sys


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "/mesonet/data/iemre/%s_ifc_daily.nc" % (ts.year, )
    nc = netCDF4.Dataset(fp, 'w')
    nc.title = "IFC Daily Precipitation %s" % (ts.year,)
    nc.platform = "Grided Estimates"
    nc.description = "Iowa Flood Center ~0.004 degree grid"
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
    nc.createDimension('lat', 1057)
    nc.createDimension('lon', 1741)
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
    lat[:] = 40.133331 + np.arange(1057) * 0.004167

    lon = nc.createVariable('lon', np.float, ('lon',))
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.bounds = "lon_bnds"
    lon.axis = "X"
    lon[:] = -97.154167 + np.arange(1741) * 0.004167

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
