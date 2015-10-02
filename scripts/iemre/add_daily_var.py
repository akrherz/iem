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

    nc.sync()
    nc.close()
