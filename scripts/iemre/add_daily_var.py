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
    rsds = nc.createVariable('rsds', np.float, ('time', 'lat', 'lon'),
                             fill_value=1.e20)
    rsds.units = "W m-2"
    rsds.long_name = 'surface_downwelling_shortwave_flux_in_air'
    rsds.standard_name = 'surface_downwelling_shortwave_flux_in_air'
    rsds.coordinates = "lon lat"
    rsds.description = "Global Shortwave Irradiance"
    nc.sync()
    nc.close()
