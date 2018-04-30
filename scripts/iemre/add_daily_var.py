"""Add a variable"""
from __future__ import print_function
import os

import netCDF4
import numpy as np
from pyiem import iemre


def main():
    """go Main go"""
    for yr in range(1893, 2016):
        fn = iemre.get_daily_ncname(yr)
        if not os.path.isfile(fn):
            print("Miss %s" % (fn, ))
            continue
        print(fn)
        nc = netCDF4.Dataset(fn, 'a')
        v1 = nc.createVariable('avg_dwpk', np.float, ('time', 'lat', 'lon'),
                               fill_value=1.e20)
        v1.units = 'K'
        v1.long_name = '2m Average Dew Point Temperature'
        v1.standard_name = 'Dewpoint'
        v1.coordinates = "lon lat"
        v1.description = ("Dew Point average computed "
                          "by averaging mixing ratios")

        v2 = nc.createVariable('wind_speed', np.float, ('time', 'lat', 'lon'),
                               fill_value=1.e20)
        v2.units = 'm s-1'
        v2.long_name = 'Wind Speed'
        v2.standard_name = 'Wind Speed'
        v2.coordinates = "lon lat"
        v2.description = "Daily averaged wind speed magnitude"

        nc.sync()
        nc.close()


if __name__ == '__main__':
    main()
