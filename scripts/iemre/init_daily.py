# Generate the IEMRE hourly analysis file for a year

import constants
import netCDF3
import mx.DateTime
import numpy
import sys

def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "/mesonet/data/iemre/%s_daily.nc" % (ts.year, )
    nc = netCDF3.Dataset(fp, 'w')
    nc.title         = "IEM Daily Reanalysis %s" % (ts.year,)
    nc.platform      = "Grided Observations"
    nc.description   = "IEM hourly analysis on a ~25 km grid"
    nc.institution   = "Iowa State University, Ames, IA, USA"
    nc.source        = "Iowa Environmental Mesonet"
    nc.project_id    = "IEM"
    nc.realization   = 1
    nc.Conventions   = 'CF-1.0'
    nc.contact       = "Daryl Herzmann, akrherz@iastate.edu, 515-294-5978"
    nc.history       = "%s Generated" % (mx.DateTime.now().strftime("%d %B %Y"),)
    nc.comment       = "No Comment at this time"



    # Setup Dimensions
    nc.createDimension('lat', constants.NY)
    nc.createDimension('lon', constants.NX)
    days = ((ts + mx.DateTime.RelativeDateTime(years=1)) - ts).days
    nc.createDimension('time', int(days) ) 

    # Setup Coordinate Variables
    lat = nc.createVariable('lat', numpy.float, ('lat',) )
    lat.units = "degrees_north"
    lat.long_name = "Latitude"
    lat.standard_name = "latitude"
    lat.axis = "Y"
    lat[:] = constants.YAXIS

    lon = nc.createVariable('lon', numpy.float, ('lon',) )
    lon.units = "degrees_east"
    lon.long_name = "Longitude"
    lon.standard_name = "longitude"
    lon.axis = "X"
    lon[:] = constants.XAXIS

    tm = nc.createVariable('time', numpy.float, ('time',) )
    tm.units = "Days since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = numpy.arange(0, int(days) )

    # Tracked variables
    high = nc.createVariable('high_tmpk', numpy.float, ('time', 'lat', 'lon'))
    high.units = "K"
    high.long_name = "2m Air Temperature Daily High"
    high.standard_name = "2m Air Temperature"
    high._FillValue = 1.e20
    high.coordinates = "lon lat"

    low = nc.createVariable('low_tmpk', numpy.float, ('time', 'lat', 'lon'))
    low.units = "K"
    low.long_name = "2m Air Temperature Daily Low"
    low.standard_name = "2m Air Temperature"
    low._FillValue = 1.e20
    low.coordinates = "lon lat"

    p01d = nc.createVariable('p01d', numpy.float, ('time','lat','lon'))
    p01d.units = 'mm'
    p01d._FillValue = 1.e20
    p01d.long_name = 'Precipitation'
    p01d.standard_name = 'Precipitation'
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    nc.close()

init_year(mx.DateTime.DateTime(int(sys.argv[1]),1,1))
