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
    nc.sync()
    nc.close()
