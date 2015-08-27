import netCDF4
import os
import numpy as np

for yr in range(1893, 2016):
    fn = "/mesonet/data/iemre/%s_mw_daily.nc" % (yr, )
    if not os.path.isfile(fn):
        print 'Miss', fn
        continue
    print fn
    nc = netCDF4.Dataset(fn, 'a')
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

    nc.sync()
    nc.close()
