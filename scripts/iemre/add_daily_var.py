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
    rsds = nc.createVariable('p01d_12z', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    rsds.units = "mm"
    rsds.long_name = 'Precipitation'
    rsds.standard_name = 'Precipitation'
    rsds.coordinates = "lon lat"
    rsds.description = "24 Hour Precipitation Ending 12 UTC"
    nc.sync()
    nc.close()
