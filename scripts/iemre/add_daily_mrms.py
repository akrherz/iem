'''
 Generate the storage netcdf file for 0.01deg MRMS data over the Midwest
'''

import datetime
import sys

import numpy as np
from pyiem import iemre
from pyiem.util import ncopen


def init_year(ts):
    """
    Create a new NetCDF file for a year of our specification!
    """

    fp = iemre.get_daily_mrms_ncname(ts.year)
    nc = ncopen(fp, 'a', timeout=300)

    nc.createDimension('nv', 2)

    lat = nc.variables['lat']
    lat.bounds = "lat_bnds"
    lat[:] = np.arange(iemre.SOUTH + 0.005, iemre.NORTH, 0.01)

    lat_bnds = nc.createVariable('lat_bnds', np.float, ('lat', 'nv'))
    lat_bnds[:, 0] = np.arange(iemre.SOUTH, iemre.NORTH, 0.01)
    lat_bnds[:, 1] = np.arange(iemre.SOUTH + 0.01, iemre.NORTH + 0.01, 0.01)

    lon = nc.variables['lon']
    lon.bounds = "lon_bnds"
    lon[:] = np.arange(iemre.WEST, iemre.EAST, 0.01)

    lon_bnds = nc.createVariable('lon_bnds', np.float, ('lon', 'nv'))
    lon_bnds[:, 0] = np.arange(iemre.WEST, iemre.EAST, 0.01)
    lon_bnds[:, 1] = np.arange(iemre.WEST + 0.01, iemre.EAST + 0.01, 0.01)

    nc.close()


if __name__ == '__main__':
    init_year(datetime.datetime(int(sys.argv[1]), 1, 1))
