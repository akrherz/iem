# Generate the IEMRE hourly analysis file for a year

import constants
import netCDF3
import mx.DateTime
import numpy

def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "/mesonet/data/iemre/%s_hourly.nc" % (ts.year, )
    nc = netCDF3.Dataset(fp, 'w')
    nc.title         = "IEM Hourly Reanalysis %s" % (ts.year,)
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
    nc.createDimension('time', int(days) * 24) 

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
    tm.units = "Hours since %s-01-01 00:00:0.0" % (ts.year,)
    tm.long_name = "Time"
    tm.standard_name = "time"
    tm.axis = "T"
    tm.calendar = "gregorian"
    tm[:] = numpy.arange(0, int(days) * 24)

    # Tracked variables
    skyc = nc.createVariable('skyc', numpy.float, ('time', 'lat', 'lon'))
    skyc.long_name = "ASOS Sky Coverage"
    skyc.stanard_name = "ASOS Sky Coverage"
    skyc.units = "%"
    skyc.valid_range = [0,100]
    skyc._FillValue = 1.e20
    skyc.coordinates = "lon lat"

    tmpk = nc.createVariable('tmpk', numpy.float, ('time', 'lat', 'lon'))
    tmpk.units = "K"
    tmpk.long_name = "2m Air Temperature"
    tmpk.standard_name = "2m Air Temperature"
    tmpk._FillValue = 1.e20
    tmpk.coordinates = "lon lat"

    dwpk = nc.createVariable('dwpf', numpy.float, ('time', 'lat', 'lon'))
    dwpk.units = "K"
    dwpk.long_name = "2m Air Dew Point Temperature"
    dwpk.standard_name = "2m Air Dew Point Temperature"
    dwpk._FillValue = 1.e20
    dwpk.coordinates = "lon lat"

    uwnd = nc.createVariable('uwnd', numpy.float, ('time', 'lat', 'lon'))
    uwnd.units = "meters per second"
    uwnd.long_name = "U component of the wind"
    uwnd.standard_name = "U component of the wind"
    uwnd._FillValue = 1.e20
    uwnd.coordinates = "lon lat"

    vwnd = nc.createVariable('vwnd', numpy.float, ('time', 'lat', 'lon'))
    vwnd.units = "meters per second"
    vwnd.long_name = "V component of the wind"
    vwnd.standard_name = "V component of the wind"
    vwnd._FillValue = 1.e20
    vwnd.coordinates = "lon lat"

    p01m = nc.createVariable('p01m', numpy.float, ('time','lat','lon'))
    p01m.units = 'mm'
    p01m._FillValue = 1.e20
    p01m.long_name = 'Precipitation'
    p01m.standard_name = 'Precipitation'
    p01m.coordinates = "lon lat"
    p01m.description = "Precipitation accumulation for the hour valid time"

    nc.close()

init_year(mx.DateTime.DateTime(2010,1,1))
