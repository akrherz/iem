# Generate the IEMRE daily analysis file for a year

from pyiem import iemre
import netCDF4
import datetime
import numpy as np
import sys


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = "/mesonet/data/iemre/%s_mw_daily.nc" % (ts.year, )
    nc = netCDF4.Dataset(fp, 'w')
    nc.title = "IEM Daily Reanalysis %s" % (ts.year,)
    nc.platform = "Grided Observations"
    nc.description = "IEM daily analysis on a 0.25 degree grid"
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
    nc.createDimension('lat', iemre.NY)
    nc.createDimension('lon', iemre.NX)
    days = ((ts.replace(year=ts.year+1)) - ts).days
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

    high12 = nc.createVariable('high_tmpk_12z', np.float,
                               ('time', 'lat', 'lon'),
                               fill_value=1.e20)
    high12.units = "K"
    high12.long_name = "2m Air Temperature 24 Hour Max at 12 UTC"
    high12.standard_name = "2m Air Temperature"
    high12.coordinates = "lon lat"

    low12 = nc.createVariable('low_tmpk_12z', np.float,
                              ('time', 'lat', 'lon'),
                              fill_value=1.e20)
    low12.units = "K"
    low12.long_name = "2m Air Temperature 12 Hour Min at 12 UTC"
    low12.standard_name = "2m Air Temperature"
    low12.coordinates = "lon lat"

    p01d = nc.createVariable('p01d', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    p01d.units = 'mm'
    p01d.long_name = 'Precipitation'
    p01d.standard_name = 'Precipitation'
    p01d.coordinates = "lon lat"
    p01d.description = "Precipitation accumulation for the day"

    p01d12 = nc.createVariable('p01d_12z', np.float, ('time', 'lat', 'lon'),
                               fill_value=1.e20)
    p01d12.units = 'mm'
    p01d12.long_name = 'Precipitation'
    p01d12.standard_name = 'Precipitation'
    p01d12.coordinates = "lon lat"
    p01d12.description = "24 Hour Precipitation Ending 12 UTC"

    rsds = nc.createVariable('rsds', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    rsds.units = "W m-2"
    rsds.long_name = 'surface_downwelling_shortwave_flux_in_air'
    rsds.standard_name = 'surface_downwelling_shortwave_flux_in_air'
    rsds.coordinates = "lon lat"
    rsds.description = "Global Shortwave Irradiance"

    snow = nc.createVariable('snow_12z', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    snow.units = 'mm'
    snow.long_name = 'Snowfall'
    snow.standard_name = 'Snowfall'
    snow.coordinates = "lon lat"
    snow.description = "Snowfall accumulation for the day"

    snowd = nc.createVariable('snowd_12z', np.float, ('time', 'lat', 'lon'),
                              fill_value=1.e20)
    snowd.units = 'mm'
    snowd.long_name = 'Snow Depth'
    snowd.standard_name = 'Snow Depth'
    snowd.coordinates = "lon lat"
    snowd.description = "Snow depth at time of observation"

    v = nc.createVariable('avg_dwpk', np.float, ('time', 'lat', 'lon'),
                          fill_value=1.e20)
    v.units = 'K'
    v.long_name = '2m Average Dew Point Temperature'
    v.standard_name = 'Dewpoint'
    v.coordinates = "lon lat"
    v.description = "Dew Point average computed by averaging mixing ratios"

    v2 = nc.createVariable('wind_speed', np.float, ('time', 'lat', 'lon'),
                           fill_value=1.e20)
    v2.units = 'm s-1'
    v2.long_name = 'Wind Speed'
    v2.standard_name = 'Wind Speed'
    v2.coordinates = "lon lat"
    v2.description = "Daily averaged wind speed magnitude"

    nc.close()

if __name__ == '__main__':
    init_year(datetime.datetime(int(sys.argv[1]), 1, 1))
